"""Transport wrappers that return RawResponse instead of parsed APIResponse.

Used by ``client.with_raw_response`` to reuse the same resource classes
without creating separate Raw*Resource wrappers (transport-swapping pattern).
"""

from __future__ import annotations

from typing import Any

from neo_tariff._http import AsyncHttpTransport, HttpTransport, RawResponse


class RawHttpTransport:
    """Sync transport wrapper that returns RawResponse from all methods.

    The same resource classes (RatesResource, SearchResource, etc.) work
    unchanged — they just get this transport instead of HttpTransport,
    so every call returns a non-raising :class:`RawResponse`.
    """

    def __init__(self, inner: HttpTransport) -> None:
        self._inner = inner

    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> RawResponse:
        return self._inner.request_raw(method, path, params=params, json_body=json_body)

    def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type | None = None,
    ) -> RawResponse:
        return self._inner.request_raw(method, path, params=params, json_body=json_body)

    def close(self) -> None:
        pass  # Don't close — the original client owns the connection


class RawAsyncHttpTransport:
    """Async transport wrapper that returns RawResponse from all methods.

    Same pattern as :class:`RawHttpTransport` but for async resources.
    """

    def __init__(self, inner: AsyncHttpTransport) -> None:
        self._inner = inner

    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> RawResponse:
        return await self._inner.request_raw(
            method, path, params=params, json_body=json_body
        )

    async def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type | None = None,
    ) -> RawResponse:
        return await self._inner.request_raw(
            method, path, params=params, json_body=json_body
        )

    async def close(self) -> None:
        pass  # Don't close — the original client owns the connection
