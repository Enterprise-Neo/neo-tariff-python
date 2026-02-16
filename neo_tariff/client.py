"""Synchronous Tariff API client."""

from __future__ import annotations

import os

from neo_tariff._http import HttpTransport
from neo_tariff.exceptions import NeoTariffError
from neo_tariff.resources import (
    CompareResource,
    ContextResource,
    RatesResource,
    SearchResource,
    VersionsResource,
)

DEFAULT_BASE_URL = "https://tariff-data.enterprise-neo.com"


class NeoTariff:
    """Synchronous client for the Neo Tariff API.

    Usage::

        from neo_tariff import NeoTariff

        # Auto-detect from NEO_TARIFF_API_KEY environment variable
        client = NeoTariff()

        # Or pass explicitly (overrides env var)
        client = NeoTariff(api_key="ntf_...")

        result = client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        print(result.data)

    Or as a context manager::

        with NeoTariff(api_key="ntf_...") as client:
            result = client.rates.evaluate_entry(...)
    """

    rates: RatesResource
    search: SearchResource
    context: ContextResource
    compare: CompareResource
    versions: VersionsResource

    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 2,
        default_headers: dict[str, str] | None = None,
    ) -> None:
        if api_key is None:
            api_key = os.environ.get("NEO_TARIFF_API_KEY")
        if api_key is None:
            raise NeoTariffError(
                "No API key provided. Either pass api_key= to the client "
                "or set the NEO_TARIFF_API_KEY environment variable."
            )

        if base_url is None:
            base_url = os.environ.get("NEO_TARIFF_BASE_URL")
        if base_url is None:
            base_url = DEFAULT_BASE_URL

        self._base_url = base_url
        self._http = HttpTransport(
            api_key=api_key,
            base_url=base_url,
            timeout=timeout,
            max_retries=max_retries,
            default_headers=default_headers,
        )
        self.rates = RatesResource(self._http)
        self.search = SearchResource(self._http)
        self.context = ContextResource(self._http)
        self.compare = CompareResource(self._http)
        self.versions = VersionsResource(self._http)

    def __repr__(self) -> str:
        return f"NeoTariff(base_url={self._base_url!r})"

    @property
    def with_raw_response(self) -> NeoTariff:
        """Returns a client variant whose resource methods return RawResponse.

        Uses transport swapping: the same resource classes are reused, but
        wired with a transport that calls ``request_raw()`` instead of
        ``request()`` / ``request_typed()``.  Return type annotations on
        resource methods will technically be inaccurate — they say
        ``APIResponse`` but actually return ``RawResponse``.  This is an
        intentional trade-off for a power-user escape hatch.
        """
        from neo_tariff._raw import RawHttpTransport

        raw_client = NeoTariff.__new__(NeoTariff)
        raw_transport = RawHttpTransport(self._http)
        raw_client._http = raw_transport
        raw_client.rates = RatesResource(raw_transport)
        raw_client.search = SearchResource(raw_transport)
        raw_client.context = ContextResource(raw_transport)
        raw_client.compare = CompareResource(raw_transport)
        raw_client.versions = VersionsResource(raw_transport)
        return raw_client

    def close(self) -> None:
        """Close the underlying HTTP connection pool."""
        self._http.close()

    def __enter__(self) -> NeoTariff:
        return self

    def __exit__(self, *args: object) -> None:
        self.close()
