"""Asynchronous Tariff API client."""

from __future__ import annotations

from os import PathLike
from typing import cast

from neo_tariff._config import resolve_client_config
from neo_tariff._http import AsyncHttpTransport
from neo_tariff.resources._base import AsyncTransportLike
from neo_tariff.resources import (
    AsyncCompareResource,
    AsyncContextResource,
    AsyncRatesResource,
    AsyncSearchResource,
    AsyncVersionsResource,
)


class AsyncNeoTariff:
    """Asynchronous client for the Neo Tariff API.

    Usage::

        from neo_tariff import AsyncNeoTariff

        # Auto-detect from NEO_TARIFF_API_KEY environment variable
        client = AsyncNeoTariff()

        # Or pass explicitly (overrides env var)
        client = AsyncNeoTariff(api_key="ntf_...")

        result = await client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        print(result.data)

    Or as an async context manager::

        async with AsyncNeoTariff(api_key="ntf_...") as client:
            result = await client.rates.evaluate_entry(...)
    """

    rates: AsyncRatesResource
    search: AsyncSearchResource
    context: AsyncContextResource
    compare: AsyncCompareResource
    versions: AsyncVersionsResource
    _http: AsyncTransportLike

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
        env_file: str | PathLike[str] | None = None,
    ) -> None:
        config = resolve_client_config(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            env_file=env_file,
        )

        self._base_url = config.base_url
        self._http = AsyncHttpTransport(
            api_key=config.api_key,
            base_url=config.base_url,
            timeout=config.timeout,
            max_retries=config.max_retries,
            default_headers=default_headers,
        )
        self.rates = AsyncRatesResource(self._http)
        self.search = AsyncSearchResource(self._http)
        self.context = AsyncContextResource(self._http)
        self.compare = AsyncCompareResource(self._http)
        self.versions = AsyncVersionsResource(self._http)

    @classmethod
    def from_env_file(
        cls,
        env_file: str | PathLike[str] = ".env",
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float | None = None,
        max_retries: int | None = None,
        default_headers: dict[str, str] | None = None,
    ) -> AsyncNeoTariff:
        """Create an async client using values from a dotenv-style env file."""
        return cls(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
            env_file=env_file,
        )

    def __repr__(self) -> str:
        return f"AsyncNeoTariff(base_url={self._base_url!r})"

    @property
    def with_raw_response(self) -> AsyncNeoTariff:
        """Returns a client variant whose resource methods return RawResponse.

        Uses transport swapping: the same async resource classes are reused,
        but wired with a transport that calls ``request_raw()`` instead of
        ``request()`` / ``request_typed()``.  Return type annotations on
        resource methods will technically be inaccurate — they say
        ``APIResponse`` but actually return ``RawResponse``.  This is an
        intentional trade-off for a power-user escape hatch.
        """
        from neo_tariff._raw import RawAsyncHttpTransport

        raw_client = AsyncNeoTariff.__new__(AsyncNeoTariff)
        raw_transport = RawAsyncHttpTransport(cast(AsyncHttpTransport, self._http))
        raw_client._http = raw_transport
        raw_client.rates = AsyncRatesResource(raw_transport)
        raw_client.search = AsyncSearchResource(raw_transport)
        raw_client.context = AsyncContextResource(raw_transport)
        raw_client.compare = AsyncCompareResource(raw_transport)
        raw_client.versions = AsyncVersionsResource(raw_transport)
        return raw_client

    async def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        await self._http.close()

    async def __aenter__(self) -> AsyncNeoTariff:
        return self

    async def __aexit__(self, *args: object) -> None:
        await self.close()
