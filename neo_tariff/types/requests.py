"""Typed request models for the Tariff SDK.

These models are provided as convenience types for building structured
requests. They are NOT required — all SDK methods accept keyword arguments
directly. Use these when you want IDE autocompletion and validation on
the request side.
"""

from __future__ import annotations

from datetime import date
from typing import Any

from pydantic import BaseModel, Field

from neo_tariff.types.shared import MaterialType


# ---------------------------------------------------------------------------
# Material composition (for Section 232 evaluations)
# ---------------------------------------------------------------------------


class MaterialProcessSteel(BaseModel):
    """Processing details for steel materials (Section 232)."""

    melt_pour_country: str | None = Field(
        default=None,
        description="Country where steel was melted and poured (ISO alpha-2).",
    )


class MaterialProcessAluminum(BaseModel):
    """Processing details for aluminum materials (Section 232)."""

    primary_smelt_country: str | None = Field(
        default=None,
        description="Country where aluminum was primary smelted (ISO alpha-2).",
    )
    secondary_smelt_country: str | None = Field(
        default=None,
        description="Country where aluminum was secondary smelted (ISO alpha-2).",
    )
    most_recent_cast_country: str | None = Field(
        default=None,
        description="Country where aluminum was most recently cast (ISO alpha-2).",
    )


class MaterialComponent(BaseModel):
    """A material component for Section 232 steel/aluminum evaluations."""

    type: MaterialType = Field(
        ..., description="Material type: steel, aluminum, copper, non_us, or other."
    )
    value_usd: float | None = Field(default=None, description="Value in USD.")
    percent_of_customs_value: float | None = Field(
        default=None, description="Percentage of total customs value."
    )
    weight_kg: float = Field(default=0, description="Weight in kilograms.")
    process: MaterialProcessSteel | MaterialProcessAluminum | dict[str, Any] | None = (
        Field(default=None, description="Processing details for the material.")
    )


# ---------------------------------------------------------------------------
# Calculation request models
# ---------------------------------------------------------------------------


class CalcInputs(BaseModel):
    """Input parameters for a single tariff duty calculation.

    At minimum, ``hts_code``, ``country_of_origin``, ``cost``, and ``qty``
    are required. All other fields have sensible defaults.

    Usage::

        from neo_tariff.types.requests import CalcInputs
        inputs = CalcInputs(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10_000,
            qty=1_000,
        )
        # Pass as dict to evaluate_entry
        result = client.rates.evaluate_entry(**inputs.model_dump(exclude_none=True))
    """

    rec_id: str | None = Field(
        default=None,
        description="Client-provided identifier echoed back for record matching.",
    )
    hts_code: str = Field(
        ...,
        description="HTS code to evaluate (dotted or undotted, 4-10 digits).",
    )
    country_of_origin: str = Field(
        ...,
        description="ISO 3166-1 alpha-2 country code.",
    )
    cost: float = Field(..., description="Customs value in the specified currency.")
    qty: float = Field(..., description="Quantity in the specified unit of measure.")
    currency_code: str | None = Field(
        default=None, description="ISO 4217 currency code (default: USD)."
    )
    qty_uom: str | None = Field(
        default=None, description="Unit of measure for quantity."
    )
    hts_date: str | None = Field(
        default=None, description="Date (YYYY-MM-DD) to find effective HTS revision."
    )
    hts_year: int | None = Field(default=None, description="HTS revision year.")
    hts_version: int | None = Field(
        default=None, description="HTS revision version number."
    )
    reciprocal: bool = Field(
        default=True,
        description="Include reciprocal (Chapter 99) additional duties.",
    )
    include_rules_view: bool = Field(
        default=False,
        description="Include unified rules view alongside standard payload.",
    )
    import_date: date | str | None = Field(
        default=None, description="Import date for reciprocal rate evaluation."
    )
    rate_column: str | None = Field(
        default=None,
        description="Explicit rate column: general, special, or other.",
    )
    base_ad_valorem_rate: float | None = Field(
        default=None,
        description="Override base ad valorem rate for reciprocal rules.",
    )
    admitted_to_ftz: bool = Field(
        default=False, description="Goods admitted to a foreign trade zone."
    )
    loading_date: date | str | None = Field(
        default=None,
        description="Date goods were loaded/entered transit for reciprocity checks.",
    )
    is_donation: bool = Field(
        default=False, description="Qualifying humanitarian donation."
    )
    is_informational: bool = Field(
        default=False, description="Primarily informational materials."
    )
    is_personal_baggage: bool = Field(
        default=False, description="Personal accompanied baggage."
    )
    usmca_claim: bool = Field(default=False, description="USMCA preferential claim.")
    program_qualified: bool = Field(
        default=True, description="Declarant affirms program eligibility."
    )
    chapter98_provision: str | None = Field(
        default=None, description="Chapter 98 provision claimed."
    )
    is_civil_aircraft: bool = Field(
        default=False,
        description="Civil aircraft parts eligible for Note 35 exemptions.",
    )
    materials: list[MaterialComponent] | None = Field(
        default=None,
        description="Material components for Section 232 evaluations.",
    )
    selected_code_conditions: list[str] | None = Field(
        default=None,
        description="Rule codes for confirmed conditional exemptions.",
    )
    product_usage: str | None = Field(
        default=None,
        description="Free-text product usage for conditional exemption matching.",
    )


class CalcBatchInputs(BaseModel):
    """Batch request for evaluating multiple tariff entries.

    Usage::

        from neo_tariff.types.requests import CalcBatchInputs, CalcInputs
        batch = CalcBatchInputs(data=[
            CalcInputs(hts_code="7208.10.15", country_of_origin="CN", cost=10000, qty=1000),
            CalcInputs(hts_code="8471.30.01", country_of_origin="JP", cost=5000, qty=100),
        ])
        result = client.rates.evaluate_entries(
            data=[e.model_dump(exclude_none=True) for e in batch.data]
        )
    """

    data: list[CalcInputs] = Field(
        ...,
        min_length=1,
        max_length=1000,
        description="List of entries to process (max 1000).",
    )
    hts_date: str | None = Field(
        default=None, description="Default HTS date for all entries."
    )
    hts_year: int | None = Field(default=None, description="Default HTS year.")
    hts_version: int | None = Field(default=None, description="Default HTS version.")


class HtsContextBatchInputs(BaseModel):
    """Batch request for HTS hub context endpoint.

    Usage::

        from neo_tariff.types.requests import HtsContextBatchInputs
        req = HtsContextBatchInputs(
            hts_codes=["7208.10.15", "8471.30.01"],
            include="rates,history",
        )
        result = client.context.get_hts_hub_batch(**req.model_dump(exclude_none=True))
    """

    hts_codes: list[str] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="HTS codes to retrieve in a single request.",
    )
    include: str | None = Field(
        default=None,
        description="Optional comma-separated include selectors for hub payload.",
    )
    history_lookback: int = Field(
        default=2,
        ge=0,
        le=20,
        description="How many historical revisions to include (when requested).",
    )
    hts_date: str | None = Field(default=None, description="Date-based HTS resolution.")
    hts_year: int | None = Field(default=None, description="Explicit HTS year.")
    hts_version: int | None = Field(default=None, description="Explicit HTS version.")


class CountryBatchInputs(BaseModel):
    """Batch request for country context endpoint.

    Usage::

        from neo_tariff.types.requests import CountryBatchInputs
        req = CountryBatchInputs(identifiers=["CN", "DE", "MX"])
        result = client.context.get_countries_batch(**req.model_dump(exclude_none=True))
    """

    identifiers: list[str] = Field(
        ...,
        min_length=1,
        max_length=500,
        description="Country identifiers (ISO alpha-2, alpha-3, names).",
    )
    hts_date: str | None = Field(default=None, description="Date-based HTS resolution.")
    hts_year: int | None = Field(default=None, description="Explicit HTS year.")
    hts_version: int | None = Field(default=None, description="Explicit HTS version.")
