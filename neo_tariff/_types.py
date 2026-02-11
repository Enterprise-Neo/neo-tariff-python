"""SDK-local envelope types.

These mirror the server's APIResponse[T] contract but carry zero server
dependencies. They exist only to parse JSON returned by the API.
"""

from __future__ import annotations

from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict

from neo_tariff.exceptions import NeoTariffError

T = TypeVar("T")


class APIPagination(BaseModel):
    """Pagination metadata returned in the API envelope."""

    model_config = ConfigDict(extra="allow")

    total: int | None = None
    limit: int | None = None
    offset: int | None = None
    next_offset: int | None = None
    has_more: bool | None = None
    returned_count: int | None = None


class APIRespError(BaseModel):
    """A single structured error from the API."""

    model_config = ConfigDict(extra="allow")

    code: str = ""
    message: str = ""
    field: str | None = None


class APIMeta(BaseModel):
    """Request/response metadata from the API envelope."""

    model_config = ConfigDict(extra="allow")

    timestamp_unixts: float | None = None
    operation: str | None = None
    params: dict[str, Any] | None = None
    hts_year: int | None = None
    hts_version: int | None = None
    pagination: APIPagination | None = None
    result_count: int | None = None
    window_info: dict[str, Any] | None = None


class APIResponse(BaseModel, Generic[T]):
    """Standard API response envelope.

    On success, ``data`` contains the payload of type ``T``.
    On failure, ``errors`` contains structured error details.
    """

    model_config = ConfigDict(extra="allow")

    success: bool
    meta: APIMeta | None = None
    data: T | None = None
    errors: list[APIRespError] | None = None

    def require_data(self) -> T:
        """Return ``data`` or raise :class:`NeoTariffError` if ``None``."""
        if self.data is None:
            raise NeoTariffError("Response contained no data")
        return self.data
