"""HTTP transport layer for the Tariff SDK.

Provides :class:`HttpTransport` (sync) and :class:`AsyncHttpTransport` (async)
backed by *httpx*.  Both handle:

* API-key authentication via ``X-API-Key`` header
* Retry with exponential backoff on transient failures
* Best-effort JSON parsing (graceful handling of HTML/proxy responses)
* Raising :class:`NeoTariffHTTPError` on non-2xx and :class:`NeoTariffAPIError`
  on ``success=False`` envelopes
"""

from __future__ import annotations

import asyncio
import json
import threading
import time
from typing import Any, TypeVar

import httpx
from pydantic import TypeAdapter

from neo_tariff._types import APIMeta, APIRespError, APIResponse
from neo_tariff._version import __version__
from neo_tariff.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    NeoTariffAPIError,
    NeoTariffConnectionError,
    NeoTariffHTTPError,
    NeoTariffError,
    ValidationError,
)

T = TypeVar("T")

_USER_AGENT = f"neo-tariff-python/{__version__}"

# Status codes that are safe to retry (transient server/infra errors).
_RETRY_STATUS_CODES = {408, 429, 500, 502, 503, 504}


def _clean(d: dict[str, Any]) -> dict[str, Any]:
    """Remove ``None``-valued keys from *d*."""
    return {k: v for k, v in d.items() if v is not None}


# ── TypeAdapter cache ────────────────────────────────────────────────────────

_adapter_cache: dict[type, TypeAdapter] = {}
_adapter_lock = threading.Lock()


def _get_adapter(response_type: type[T]) -> TypeAdapter:
    """Get or create a cached TypeAdapter for ``APIResponse[response_type]``."""
    if response_type not in _adapter_cache:
        with _adapter_lock:
            if response_type not in _adapter_cache:  # double-check after lock
                _adapter_cache[response_type] = TypeAdapter(
                    APIResponse[response_type]  # type: ignore[valid-type]
                )
    return _adapter_cache[response_type]


# ── Shared helpers ───────────────────────────────────────────────────────────


def _parse_envelope(
    body: dict[str, Any] | None,
) -> tuple[
    APIMeta | None,
    list[APIRespError] | None,
    str,
]:
    """Best-effort parse meta/errors from a JSON body dict.

    Returns ``(meta, errors, message)``.
    """
    if body is None:
        return None, None, "Unknown error"
    meta = None
    errors = None
    message = "API error"
    try:
        if "meta" in body and body["meta"] is not None:
            meta = APIMeta.model_validate(body["meta"])
    except Exception:
        pass  # Best-effort: malformed meta shouldn't prevent error reporting
    try:
        if "errors" in body and body["errors"] is not None:
            errors = [APIRespError.model_validate(e) for e in body["errors"]]
            if errors:
                message = errors[0].message or message
    except Exception:
        pass  # Best-effort: malformed errors shouldn't prevent error reporting
    if "detail" in body:
        detail = body["detail"]
        if isinstance(detail, str):
            message = detail
        elif isinstance(detail, list) and detail:
            first = detail[0]
            message = (
                first.get("msg", message) if isinstance(first, dict) else str(first)
            )
    return meta, errors, message


def _make_http_error(
    status_code: int,
    body: dict[str, Any] | None,
    raw_text: str,
) -> NeoTariffHTTPError:
    """Create the appropriate HTTP error subclass."""
    meta, errors, message = _parse_envelope(body)
    kwargs: dict[str, Any] = dict(
        status_code=status_code,
        errors=errors,
        meta=meta,
        raw_body=raw_text,
    )
    if status_code in (401, 403):
        return AuthenticationError(message, **kwargs)
    if status_code == 404:
        return NotFoundError(message, **kwargs)
    if status_code == 422:
        return ValidationError(message, **kwargs)
    if status_code == 429:
        return RateLimitError(message, **kwargs)
    if status_code >= 500:
        return ServerError(message, **kwargs)
    return NeoTariffHTTPError(message, **kwargs)


def _make_api_error(
    status_code: int,
    parsed: APIResponse,  # type: ignore[type-arg]
) -> NeoTariffAPIError:
    """Create a NeoTariffAPIError from a ``success=False`` envelope."""
    message = "API returned success=False"
    if parsed.errors:
        message = parsed.errors[0].message or message
    return NeoTariffAPIError(
        message,
        status_code=status_code,
        errors=parsed.errors,
        meta=parsed.meta,
    )


def _handle_response_data(response: httpx.Response) -> APIResponse[Any]:
    """Shared response-handling logic (sync and async use the same flow)."""
    body: dict[str, Any] | None = None
    raw_text = response.text
    try:
        body = response.json()
    except (json.JSONDecodeError, ValueError):
        pass  # Non-JSON response (e.g. HTML proxy error); body stays None

    if response.status_code >= 400:
        raise _make_http_error(response.status_code, body, raw_text)

    if body is None:
        raise NeoTariffError(f"Expected JSON response, got: {raw_text[:200]}")

    parsed: APIResponse[Any] = APIResponse.model_validate(body)

    if not parsed.success:
        raise _make_api_error(response.status_code, parsed)

    return parsed


def _handle_typed_response(
    response: httpx.Response,
    response_type: type[T],
) -> APIResponse[T]:
    """Parse response with a specific data type using cached TypeAdapter."""
    body: dict[str, Any] | None = None
    raw_text = response.text
    try:
        body = response.json()
    except (json.JSONDecodeError, ValueError):
        pass  # Non-JSON response (e.g. HTML proxy error); body stays None

    if response.status_code >= 400:
        raise _make_http_error(response.status_code, body, raw_text)

    if body is None:
        raise NeoTariffError(f"Expected JSON response, got: {raw_text[:200]}")

    adapter = _get_adapter(response_type)
    parsed: APIResponse[T] = adapter.validate_python(body)

    if not parsed.success:
        raise _make_api_error(response.status_code, parsed)

    return parsed


def _compute_backoff(
    attempt: int,
    response: httpx.Response | None,
) -> float:
    """Compute backoff duration respecting Retry-After header."""
    backoff = min(2**attempt * 0.5, 8.0)
    if response is not None:
        retry_after = response.headers.get("Retry-After")
        if retry_after:
            try:
                backoff = max(backoff, float(retry_after))
            except ValueError:
                pass  # Invalid Retry-After header; use computed backoff
    return backoff


# ── Raw response wrapper ────────────────────────────────────────────────────


class RawResponse:
    """Non-raising wrapper for power users who need the raw httpx response."""

    def __init__(
        self,
        http_response: httpx.Response,
        parsed: APIResponse[Any] | None,
    ) -> None:
        self.http_response = http_response
        self.parsed = parsed


def _make_raw(response: httpx.Response) -> RawResponse:
    body: dict[str, Any] | None = None
    try:
        body = response.json()
    except Exception:
        pass  # Best-effort JSON parsing; body stays None for non-JSON responses
    parsed: APIResponse[Any] | None = None
    if body is not None:
        try:
            parsed = APIResponse.model_validate(body)
        except Exception:
            pass  # Best-effort envelope parsing; parsed stays None if schema doesn't match
    return RawResponse(http_response=response, parsed=parsed)


# ── Sync transport ──────────────────────────────────────────────────────────


class HttpTransport:
    """Synchronous HTTP transport backed by :class:`httpx.Client`.

    Retries transient failures (status 408/429/500/502/503/504 and network
    errors) with exponential backoff.

    .. note::
        All TRD endpoints are pure computation/lookups with no side effects,
        so POST retries are safe.  If the API ever adds mutating endpoints,
        revisit this assumption.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self._client = httpx.Client(
            base_url=base_url,
            headers={
                "X-API-Key": api_key,
                "User-Agent": _USER_AGENT,
                "Accept": "application/json",
            },
            timeout=timeout,
        )
        self._max_retries = max_retries

    # -- internal retry loop --

    def _send_with_retries(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Execute an HTTP request with retry logic."""
        last_exc: Exception | None = None
        response: httpx.Response | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = self._client.request(
                    method, path, params=params, json=json_body
                )
                if response.status_code not in _RETRY_STATUS_CODES:
                    return response
                last_exc = None
            except httpx.TransportError as exc:
                last_exc = exc
                response = None

            # Backoff before retry (skip on last attempt)
            if attempt < self._max_retries:
                backoff = _compute_backoff(attempt, response)
                time.sleep(backoff)

        if last_exc is not None:
            raise NeoTariffConnectionError(
                f"Request failed after {self._max_retries + 1} attempts: {last_exc}"
            ) from last_exc

        # response is not None here — it had a retryable status code
        assert response is not None
        return response

    # -- public API --

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> APIResponse[Any]:
        """Make a request and return the parsed envelope.

        Raises on HTTP errors, network errors, and ``success=False``.
        """
        response = self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _handle_response_data(response)

    def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type[T],
    ) -> APIResponse[T]:
        """Make a request and return a typed parsed envelope."""
        response = self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _handle_typed_response(response, response_type)

    def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> RawResponse:
        """Make a request returning a non-raising :class:`RawResponse`."""
        response = self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _make_raw(response)

    def close(self) -> None:
        self._client.close()


# ── Async transport ─────────────────────────────────────────────────────────


class AsyncHttpTransport:
    """Asynchronous HTTP transport backed by :class:`httpx.AsyncClient`.

    Retries transient failures with exponential backoff (same policy as sync).

    .. note::
        All TRD endpoints are pure computation/lookups with no side effects,
        so POST retries are safe.
    """

    def __init__(
        self,
        *,
        api_key: str,
        base_url: str,
        timeout: float = 30.0,
        max_retries: int = 2,
    ) -> None:
        self._client = httpx.AsyncClient(
            base_url=base_url,
            headers={
                "X-API-Key": api_key,
                "User-Agent": _USER_AGENT,
                "Accept": "application/json",
            },
            timeout=timeout,
        )
        self._max_retries = max_retries

    # -- internal retry loop --

    async def _send_with_retries(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """Execute an HTTP request with retry logic."""
        last_exc: Exception | None = None
        response: httpx.Response | None = None

        for attempt in range(self._max_retries + 1):
            try:
                response = await self._client.request(
                    method, path, params=params, json=json_body
                )
                if response.status_code not in _RETRY_STATUS_CODES:
                    return response
                last_exc = None
            except httpx.TransportError as exc:
                last_exc = exc
                response = None

            # Backoff before retry (skip on last attempt)
            if attempt < self._max_retries:
                backoff = _compute_backoff(attempt, response)
                await asyncio.sleep(backoff)

        if last_exc is not None:
            raise NeoTariffConnectionError(
                f"Request failed after {self._max_retries + 1} attempts: {last_exc}"
            ) from last_exc

        assert response is not None
        return response

    # -- public API --

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> APIResponse[Any]:
        response = await self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _handle_response_data(response)

    async def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type[T],
    ) -> APIResponse[T]:
        """Make a request and return a typed parsed envelope."""
        response = await self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _handle_typed_response(response, response_type)

    async def request_raw(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> RawResponse:
        response = await self._send_with_retries(
            method, path, params=params, json_body=json_body
        )
        return _make_raw(response)

    async def close(self) -> None:
        await self._client.aclose()
