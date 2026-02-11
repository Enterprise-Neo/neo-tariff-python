"""Rates resource – tariff duty calculation endpoints."""

from __future__ import annotations

from datetime import date
from typing import Any

from neo_tariff._http import _clean
from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.rates import CalcResponse


class RatesResource(SyncResource):
    """Synchronous rates resource."""

    def evaluate_entry(
        self,
        *,
        hts_code: str,
        country_of_origin: str,
        cost: float,
        qty: float,
        rec_id: str | None = None,
        currency_code: str | None = None,
        qty_uom: str | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        reciprocal: bool = True,
        include_rules_view: bool = False,
        import_date: date | str | None = None,
        rate_column: str | None = None,
        base_ad_valorem_rate: float | None = None,
        admitted_to_ftz: bool = False,
        loading_date: date | str | None = None,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        chapter98_provision: str | None = None,
        is_civil_aircraft: bool = False,
        materials: list[dict[str, Any]] | None = None,
        selected_code_conditions: list[str] | None = None,
        product_usage: str | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[CalcResponse]:
        """Evaluate duty for a single HTS entry.

        Calls ``POST /rates/entry``.
        """
        body = _clean(
            {
                "hts_code": hts_code,
                "country_of_origin": country_of_origin,
                "cost": cost,
                "qty": qty,
                "rec_id": rec_id,
                "currency_code": currency_code,
                "qty_uom": qty_uom,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
                "reciprocal": reciprocal,
                "include_rules_view": include_rules_view,
                "import_date": str(import_date) if import_date else None,
                "rate_column": rate_column,
                "base_ad_valorem_rate": base_ad_valorem_rate,
                "admitted_to_ftz": admitted_to_ftz,
                "loading_date": str(loading_date) if loading_date else None,
                "is_donation": is_donation,
                "is_informational": is_informational,
                "is_personal_baggage": is_personal_baggage,
                "usmca_claim": usmca_claim,
                "program_qualified": program_qualified,
                "chapter98_provision": chapter98_provision,
                "is_civil_aircraft": is_civil_aircraft,
                "materials": materials,
                "selected_code_conditions": selected_code_conditions,
                "product_usage": product_usage,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return self._http.request_typed(
            "POST",
            "/rates/entry",
            json_body=body,
            params=params or None,
            response_type=CalcResponse,
        )

    def evaluate_entries(
        self,
        *,
        data: list[dict[str, Any]],
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[list[CalcResponse]]:
        """Evaluate duty for a batch of entries (max 1000).

        Calls ``POST /rates/entries``.
        """
        body = _clean(
            {
                "data": data,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return self._http.request_typed(
            "POST",
            "/rates/entries",
            json_body=body,
            params=params or None,
            response_type=list[CalcResponse],
        )

    def evaluate_multicountry(
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
        reciprocal: bool = True,
        include_rules_view: bool = False,
        import_date: date | str | None = None,
        loading_date: date | str | None = None,
        rate_column: str | None = None,
        base_ad_valorem_rate: float | None = None,
        admitted_to_ftz: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        chapter98_provision: str | None = None,
        materials: list[dict[str, Any]] | None = None,
        selected_code_conditions: list[str] | None = None,
        product_usage: str | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[list[CalcResponse]]:
        """Evaluate duty across multiple countries for a single HTS code.

        Calls ``POST /rates/multicountry``.
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
                "reciprocal": reciprocal,
                "include_rules_view": include_rules_view,
                "import_date": str(import_date) if import_date else None,
                "loading_date": str(loading_date) if loading_date else None,
                "rate_column": rate_column,
                "base_ad_valorem_rate": base_ad_valorem_rate,
                "admitted_to_ftz": admitted_to_ftz,
                "usmca_claim": usmca_claim,
                "program_qualified": program_qualified,
                "is_donation": is_donation,
                "is_informational": is_informational,
                "is_personal_baggage": is_personal_baggage,
                "chapter98_provision": chapter98_provision,
                "materials": materials,
                "selected_code_conditions": selected_code_conditions,
                "product_usage": product_usage,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return self._http.request_typed(
            "POST",
            "/rates/multicountry",
            json_body=body,
            params=params or None,
            response_type=list[CalcResponse],
        )


class AsyncRatesResource(AsyncResource):
    """Asynchronous rates resource."""

    async def evaluate_entry(
        self,
        *,
        hts_code: str,
        country_of_origin: str,
        cost: float,
        qty: float,
        rec_id: str | None = None,
        currency_code: str | None = None,
        qty_uom: str | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        reciprocal: bool = True,
        include_rules_view: bool = False,
        import_date: date | str | None = None,
        rate_column: str | None = None,
        base_ad_valorem_rate: float | None = None,
        admitted_to_ftz: bool = False,
        loading_date: date | str | None = None,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        chapter98_provision: str | None = None,
        is_civil_aircraft: bool = False,
        materials: list[dict[str, Any]] | None = None,
        selected_code_conditions: list[str] | None = None,
        product_usage: str | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[CalcResponse]:
        """Evaluate duty for a single HTS entry.

        Calls ``POST /rates/entry``.
        """
        body = _clean(
            {
                "hts_code": hts_code,
                "country_of_origin": country_of_origin,
                "cost": cost,
                "qty": qty,
                "rec_id": rec_id,
                "currency_code": currency_code,
                "qty_uom": qty_uom,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
                "reciprocal": reciprocal,
                "include_rules_view": include_rules_view,
                "import_date": str(import_date) if import_date else None,
                "rate_column": rate_column,
                "base_ad_valorem_rate": base_ad_valorem_rate,
                "admitted_to_ftz": admitted_to_ftz,
                "loading_date": str(loading_date) if loading_date else None,
                "is_donation": is_donation,
                "is_informational": is_informational,
                "is_personal_baggage": is_personal_baggage,
                "usmca_claim": usmca_claim,
                "program_qualified": program_qualified,
                "chapter98_provision": chapter98_provision,
                "is_civil_aircraft": is_civil_aircraft,
                "materials": materials,
                "selected_code_conditions": selected_code_conditions,
                "product_usage": product_usage,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return await self._http.request_typed(
            "POST",
            "/rates/entry",
            json_body=body,
            params=params or None,
            response_type=CalcResponse,
        )

    async def evaluate_entries(
        self,
        *,
        data: list[dict[str, Any]],
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[list[CalcResponse]]:
        """Evaluate duty for a batch of entries (max 1000).

        Calls ``POST /rates/entries``.
        """
        body = _clean(
            {
                "data": data,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return await self._http.request_typed(
            "POST",
            "/rates/entries",
            json_body=body,
            params=params or None,
            response_type=list[CalcResponse],
        )

    async def evaluate_multicountry(
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
        reciprocal: bool = True,
        include_rules_view: bool = False,
        import_date: date | str | None = None,
        loading_date: date | str | None = None,
        rate_column: str | None = None,
        base_ad_valorem_rate: float | None = None,
        admitted_to_ftz: bool = False,
        usmca_claim: bool = False,
        program_qualified: bool = True,
        is_donation: bool = False,
        is_informational: bool = False,
        is_personal_baggage: bool = False,
        chapter98_provision: str | None = None,
        materials: list[dict[str, Any]] | None = None,
        selected_code_conditions: list[str] | None = None,
        product_usage: str | None = None,
        include_debug: bool = False,
        include_reciprocal_debug: bool = False,
    ) -> APIResponse[list[CalcResponse]]:
        """Evaluate duty across multiple countries for a single HTS code.

        Calls ``POST /rates/multicountry``.
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
                "reciprocal": reciprocal,
                "include_rules_view": include_rules_view,
                "import_date": str(import_date) if import_date else None,
                "loading_date": str(loading_date) if loading_date else None,
                "rate_column": rate_column,
                "base_ad_valorem_rate": base_ad_valorem_rate,
                "admitted_to_ftz": admitted_to_ftz,
                "usmca_claim": usmca_claim,
                "program_qualified": program_qualified,
                "is_donation": is_donation,
                "is_informational": is_informational,
                "is_personal_baggage": is_personal_baggage,
                "chapter98_provision": chapter98_provision,
                "materials": materials,
                "selected_code_conditions": selected_code_conditions,
                "product_usage": product_usage,
            }
        )
        params = _clean(
            {
                "include_debug": include_debug or None,
                "include_reciprocal_debug": include_reciprocal_debug or None,
            }
        )
        return await self._http.request_typed(
            "POST",
            "/rates/multicountry",
            json_body=body,
            params=params or None,
            response_type=list[CalcResponse],
        )
