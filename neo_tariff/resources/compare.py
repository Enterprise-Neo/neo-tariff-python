"""Compare resource – tariff comparison and version diff endpoints."""

from __future__ import annotations

from neo_tariff._http import _clean
from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.compare import CompareRatesResponse, CompareSourcesResponse
from neo_tariff.types.rates import CalcResponse


class CompareResource(SyncResource):
    """Synchronous compare resource."""

    def tariff(
        self,
        *,
        hts_code: str,
        countries: list[str],
        cost: float,
        qty: float,
        currency_code: str | None = None,
        qty_uom: str | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[dict[str, CalcResponse]]:
        """Compare tariff rates across countries for an HTS code.

        Calls ``POST /compare/tariff``.
        """
        body = _clean(
            {
                "hts_code": hts_code,
                "countries": countries,
                "cost": cost,
                "qty": qty,
                "currency_code": currency_code,
                "qty_uom": qty_uom,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "POST",
            "/compare/tariff",
            json_body=body,
            response_type=dict[str, CalcResponse],
        )

    def hts_rates(
        self,
        hts_code: str,
        *,
        year_a: int,
        version_a: int,
        year_b: int | None = None,
        version_b: int | None = None,
        include_summary: bool = False,
    ) -> APIResponse[CompareRatesResponse]:
        """Compare HTS rates between two source versions.

        Calls ``GET /compare/hts/{hts_code}``.
        """
        params = _clean(
            {
                "year_a": year_a,
                "version_a": version_a,
                "year_b": year_b,
                "version_b": version_b,
                "include_summary": include_summary or None,
            }
        )
        return self._http.request_typed(
            "GET",
            f"/compare/hts/{hts_code}",
            params=params,
            response_type=CompareRatesResponse,
        )

    def sources(
        self,
        *,
        year_a: int,
        version_a: int,
        year_b: int | None = None,
        version_b: int | None = None,
        include_summary: bool = False,
    ) -> APIResponse[CompareSourcesResponse]:
        """Compare two HTS source versions.

        Calls ``GET /compare/sources``.
        """
        params = _clean(
            {
                "year_a": year_a,
                "version_a": version_a,
                "year_b": year_b,
                "version_b": version_b,
                "include_summary": include_summary or None,
            }
        )
        return self._http.request_typed(
            "GET",
            "/compare/sources",
            params=params,
            response_type=CompareSourcesResponse,
        )


class AsyncCompareResource(AsyncResource):
    """Asynchronous compare resource."""

    async def tariff(
        self,
        *,
        hts_code: str,
        countries: list[str],
        cost: float,
        qty: float,
        currency_code: str | None = None,
        qty_uom: str | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[dict[str, CalcResponse]]:
        """Compare tariff rates across countries for an HTS code.

        Calls ``POST /compare/tariff``.
        """
        body = _clean(
            {
                "hts_code": hts_code,
                "countries": countries,
                "cost": cost,
                "qty": qty,
                "currency_code": currency_code,
                "qty_uom": qty_uom,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "POST",
            "/compare/tariff",
            json_body=body,
            response_type=dict[str, CalcResponse],
        )

    async def hts_rates(
        self,
        hts_code: str,
        *,
        year_a: int,
        version_a: int,
        year_b: int | None = None,
        version_b: int | None = None,
        include_summary: bool = False,
    ) -> APIResponse[CompareRatesResponse]:
        """Compare HTS rates between two source versions.

        Calls ``GET /compare/hts/{hts_code}``.
        """
        params = _clean(
            {
                "year_a": year_a,
                "version_a": version_a,
                "year_b": year_b,
                "version_b": version_b,
                "include_summary": include_summary or None,
            }
        )
        return await self._http.request_typed(
            "GET",
            f"/compare/hts/{hts_code}",
            params=params,
            response_type=CompareRatesResponse,
        )

    async def sources(
        self,
        *,
        year_a: int,
        version_a: int,
        year_b: int | None = None,
        version_b: int | None = None,
        include_summary: bool = False,
    ) -> APIResponse[CompareSourcesResponse]:
        """Compare two HTS source versions.

        Calls ``GET /compare/sources``.
        """
        params = _clean(
            {
                "year_a": year_a,
                "version_a": version_a,
                "year_b": year_b,
                "version_b": version_b,
                "include_summary": include_summary or None,
            }
        )
        return await self._http.request_typed(
            "GET",
            "/compare/sources",
            params=params,
            response_type=CompareSourcesResponse,
        )
