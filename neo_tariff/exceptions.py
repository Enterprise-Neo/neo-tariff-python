"""Exception hierarchy for the Tariff SDK.

Three layers:
- NeoTariffHTTPError: non-2xx HTTP responses (infra/proxy errors)
- NeoTariffAPIError: 2xx but success=False (API business-logic errors)
- NeoTariffConnectionError: network-level failures (timeout, DNS, etc.)

All inherit from NeoTariffError for catch-all handling.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo_tariff._types import APIMeta, APIRespError


class NeoTariffError(Exception):
    """Base exception for all SDK errors."""


# ── Layer 1: HTTP-level errors (non-2xx) ────────────────────────────────────


class NeoTariffHTTPError(NeoTariffError):
    """Non-2xx HTTP response from the API.

    Attributes:
        status_code: HTTP status code (e.g., 401, 404, 500).
        message: Human-readable error message.
        errors: Structured error list from the API response body, if available.
        meta: API metadata from the response body, if available.
        raw_body: Raw response text for debugging non-JSON errors.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int,
        errors: list[APIRespError] | None = None,
        meta: APIMeta | None = None,
        raw_body: str | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.errors = errors
        self.meta = meta
        self.raw_body = raw_body


class AuthenticationError(NeoTariffHTTPError):
    """401 or 403: Invalid or missing API key."""


class NotFoundError(NeoTariffHTTPError):
    """404: Requested resource not found."""


class ValidationError(NeoTariffHTTPError):
    """422: Request validation failed."""


class RateLimitError(NeoTariffHTTPError):
    """429: Rate limit exceeded."""


class ServerError(NeoTariffHTTPError):
    """500+: Internal server error."""


# ── Layer 2: API envelope errors (2xx but success=False) ────────────────────


class NeoTariffAPIError(NeoTariffError):
    """HTTP 2xx but the API returned success=False.

    Attributes:
        status_code: HTTP status code (typically 200).
        message: Human-readable error summary.
        errors: Structured error list from the response envelope.
        meta: API metadata from the response envelope.
    """

    def __init__(
        self,
        message: str,
        *,
        status_code: int = 200,
        errors: list[APIRespError] | None = None,
        meta: APIMeta | None = None,
    ) -> None:
        super().__init__(message)
        self.status_code = status_code
        self.message = message
        self.errors = errors
        self.meta = meta


# ── Layer 3: Network errors ─────────────────────────────────────────────────


class NeoTariffConnectionError(NeoTariffError):
    """Network-level failure: timeout, DNS resolution, connection refused."""
