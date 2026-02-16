"""Base resource classes for sync and async transports."""

from __future__ import annotations

from typing import Any, Protocol


class SyncTransportLike(Protocol):
    def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any: ...

    def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type[Any],
    ) -> Any: ...

    def close(self) -> None: ...


class AsyncTransportLike(Protocol):
    async def request(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
    ) -> Any: ...

    async def request_typed(
        self,
        method: str,
        path: str,
        *,
        params: dict[str, Any] | None = None,
        json_body: dict[str, Any] | None = None,
        response_type: type[Any],
    ) -> Any: ...

    async def close(self) -> None: ...


class SyncResource:
    """Base class for synchronous resource namespaces."""

    def __init__(self, http: SyncTransportLike) -> None:
        self._http = http


class AsyncResource:
    """Base class for asynchronous resource namespaces."""

    def __init__(self, http: AsyncTransportLike) -> None:
        self._http = http
