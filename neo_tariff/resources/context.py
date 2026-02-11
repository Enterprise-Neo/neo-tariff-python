"""Context resource – HTS structure, country, and documentation endpoints."""

from __future__ import annotations

from datetime import date
from typing import Any

from neo_tariff._http import _clean
from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.context import APIRespDataHtsCodeContext, APIRespDataHtsCodeHub
from neo_tariff.types.countries import CountryRecord


class ContextResource(SyncResource):
    """Synchronous context resource."""

    def list_sections(
        self,
        *,
        include_children: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """List all HTS sections.

        Calls ``GET /context/hts/sections``.
        """
        params = _clean(
            {
                "include_children": include_children or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request("GET", "/context/hts/sections", params=params)

    def list_chapters_by_section(
        self,
        section_name: str,
        *,
        include_context: bool = False,
        include_hts_codes: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """List chapters within a specific HTS section.

        Calls ``GET /context/hts/sections/{section_name}/chapters``.
        """
        params = _clean(
            {
                "include_context": include_context or None,
                "include_hts_codes": include_hts_codes or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request(
            "GET",
            f"/context/hts/sections/{section_name}/chapters",
            params=params,
        )

    def get_hts_code(
        self,
        hts_code: str,
        *,
        reciprocal: bool = False,
        country_of_origin: str | None = None,
        import_date: date | str | None = None,
        loading_date: date | str | None = None,
        rate_column: str | None = None,
        customs_value: float | None = None,
        quantity: float | None = None,
        admitted_to_ftz: bool = False,
        materials: str | None = None,
        include_reciprocal_debug: bool = False,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        chapter98_provision: str | None = None,
        is_civil_aircraft: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[APIRespDataHtsCodeHub]:
        """Get context for a specific HTS code with optional rate calculation.

        Calls ``GET /context/hts/{hts_code}``.
        """
        params = _clean(
            {
                "reciprocal": reciprocal or None,
                "country_of_origin": country_of_origin,
                "import_date": str(import_date) if import_date else None,
                "loading_date": str(loading_date) if loading_date else None,
                "rate_column": rate_column,
                "value": customs_value,
                "quantity": quantity,
                "admitted_to_ftz": admitted_to_ftz or None,
                "materials": materials,
                "include_reciprocal_debug": include_reciprocal_debug or None,
                "is_donation": is_donation or None,
                "is_informational": is_informational or None,
                "is_personal_baggage": is_personal_baggage or None,
                "usmca_claim": usmca_claim or None,
                "program_qualified": program_qualified
                if not program_qualified
                else None,
                "chapter98_provision": chapter98_provision,
                "is_civil_aircraft": is_civil_aircraft or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            f"/context/hts/{hts_code}",
            params=params,
            response_type=APIRespDataHtsCodeHub,
        )

    def get_hts_details(
        self,
        hts_code: str,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[APIRespDataHtsCodeContext]:
        """Get detailed information for a specific HTS code.

        Calls ``GET /context/hts/{hts_code}/details``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            f"/context/hts/{hts_code}/details",
            params=params,
            response_type=APIRespDataHtsCodeContext,
        )

    def get_hts_hub(
        self,
        hts_code: str,
        *,
        include: str | None = None,
        history_lookback: int = 2,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """Get the HTS hub view for a code (aggregated context).

        Calls ``GET /context/hts/{hts_code}/hub``.
        """
        params = _clean(
            {
                "include": include,
                "history_lookback": history_lookback,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request("GET", f"/context/hts/{hts_code}/hub", params=params)

    def list_countries(
        self,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[CountryRecord]]:
        """List all countries with tariff context.

        Calls ``GET /context/countries``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            "/context/countries",
            params=params,
            response_type=list[CountryRecord],
        )

    def get_country(
        self,
        identifier: str,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[CountryRecord]:
        """Get tariff context for a specific country.

        Calls ``GET /context/countries/{identifier}``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            f"/context/countries/{identifier}",
            params=params,
            response_type=CountryRecord,
        )


class AsyncContextResource(AsyncResource):
    """Asynchronous context resource."""

    async def list_sections(
        self,
        *,
        include_children: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """List all HTS sections.

        Calls ``GET /context/hts/sections``.
        """
        params = _clean(
            {
                "include_children": include_children or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request("GET", "/context/hts/sections", params=params)

    async def list_chapters_by_section(
        self,
        section_name: str,
        *,
        include_context: bool = False,
        include_hts_codes: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """List chapters within a specific HTS section.

        Calls ``GET /context/hts/sections/{section_name}/chapters``.
        """
        params = _clean(
            {
                "include_context": include_context or None,
                "include_hts_codes": include_hts_codes or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request(
            "GET",
            f"/context/hts/sections/{section_name}/chapters",
            params=params,
        )

    async def get_hts_code(
        self,
        hts_code: str,
        *,
        reciprocal: bool = False,
        country_of_origin: str | None = None,
        import_date: date | str | None = None,
        loading_date: date | str | None = None,
        rate_column: str | None = None,
        customs_value: float | None = None,
        quantity: float | None = None,
        admitted_to_ftz: bool = False,
        materials: str | None = None,
        include_reciprocal_debug: bool = False,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        chapter98_provision: str | None = None,
        is_civil_aircraft: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[APIRespDataHtsCodeHub]:
        """Get context for a specific HTS code with optional rate calculation.

        Calls ``GET /context/hts/{hts_code}``.
        """
        params = _clean(
            {
                "reciprocal": reciprocal or None,
                "country_of_origin": country_of_origin,
                "import_date": str(import_date) if import_date else None,
                "loading_date": str(loading_date) if loading_date else None,
                "rate_column": rate_column,
                "value": customs_value,
                "quantity": quantity,
                "admitted_to_ftz": admitted_to_ftz or None,
                "materials": materials,
                "include_reciprocal_debug": include_reciprocal_debug or None,
                "is_donation": is_donation or None,
                "is_informational": is_informational or None,
                "is_personal_baggage": is_personal_baggage or None,
                "usmca_claim": usmca_claim or None,
                "program_qualified": program_qualified
                if not program_qualified
                else None,
                "chapter98_provision": chapter98_provision,
                "is_civil_aircraft": is_civil_aircraft or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            f"/context/hts/{hts_code}",
            params=params,
            response_type=APIRespDataHtsCodeHub,
        )

    async def get_hts_details(
        self,
        hts_code: str,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[APIRespDataHtsCodeContext]:
        """Get detailed information for a specific HTS code.

        Calls ``GET /context/hts/{hts_code}/details``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            f"/context/hts/{hts_code}/details",
            params=params,
            response_type=APIRespDataHtsCodeContext,
        )

    async def get_hts_hub(
        self,
        hts_code: str,
        *,
        include: str | None = None,
        history_lookback: int = 2,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """Get the HTS hub view for a code (aggregated context).

        Calls ``GET /context/hts/{hts_code}/hub``.
        """
        params = _clean(
            {
                "include": include,
                "history_lookback": history_lookback,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request(
            "GET", f"/context/hts/{hts_code}/hub", params=params
        )

    async def list_countries(
        self,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[CountryRecord]]:
        """List all countries with tariff context.

        Calls ``GET /context/countries``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            "/context/countries",
            params=params,
            response_type=list[CountryRecord],
        )

    async def get_country(
        self,
        identifier: str,
        *,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[CountryRecord]:
        """Get tariff context for a specific country.

        Calls ``GET /context/countries/{identifier}``.
        """
        params = _clean(
            {
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            f"/context/countries/{identifier}",
            params=params,
            response_type=CountryRecord,
        )
