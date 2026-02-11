"""Base resource classes for sync and async transports."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from neo_tariff._http import AsyncHttpTransport, HttpTransport


class SyncResource:
    """Base class for synchronous resource namespaces."""

    def __init__(self, http: HttpTransport) -> None:
        self._http = http


class AsyncResource:
    """Base class for asynchronous resource namespaces."""

    def __init__(self, http: AsyncHttpTransport) -> None:
        self._http = http
