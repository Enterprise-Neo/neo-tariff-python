"""Versions resource – HTS source version listing."""

from __future__ import annotations

from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.versions import HtsSourceVersion


class VersionsResource(SyncResource):
    """Synchronous versions resource."""

    def list(self) -> APIResponse[list[HtsSourceVersion]]:
        """List all available HTS source versions.

        Calls ``GET /versions``.
        """
        return self._http.request_typed(
            "GET",
            "/versions",
            response_type=list[HtsSourceVersion],
        )


class AsyncVersionsResource(AsyncResource):
    """Asynchronous versions resource."""

    async def list(self) -> APIResponse[list[HtsSourceVersion]]:
        """List all available HTS source versions.

        Calls ``GET /versions``.
        """
        return await self._http.request_typed(
            "GET",
            "/versions",
            response_type=list[HtsSourceVersion],
        )
