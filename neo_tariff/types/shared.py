"""Shared models used across multiple resource types.

Includes HTS rate components, schedule entries, and enums that appear
in both rates and context responses.
"""

from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class RateColumn(str, Enum):
    """Tariff rate column identifier."""

    GENERAL = "general"
    SPECIAL = "special"
    OTHER = "other"
    ADDITIONAL = "additionalDuties"


class RateBasis(str, Enum):
    """Rate calculation basis."""

    FREE = "free"
    ADVALOREM = "advalorem"
    SPECIFIC = "specific"
    REFERENCE = "reference"
    FALLBACK = "fallback"


class RateUsage(str, Enum):
    """How a rate component is applied in the calculation."""

    BASE = "base"
    REPLACE = "replace"
    ADDITIVE = "additive"
    SUBTRACTIVE = "subtractive"
    IGNORE = "ignore"


class MaterialType(str, Enum):
    """Material type for Section 232 evaluations."""

    STEEL = "steel"
    ALUMINUM = "aluminum"
    COPPER = "copper"
    NON_US = "non_us"
    OTHER = "other"


# ---------------------------------------------------------------------------
# Rate component models
# ---------------------------------------------------------------------------


class SpecialRateCondition(BaseModel):
    """Special rate condition (e.g., trade agreement qualification)."""

    model_config = ConfigDict(extra="allow")

    code: str = Field(..., description="SPI code, e.g. 'AU', 'A+'.")
    program_name: str | None = Field(None, description="Full program name.")


class HtsRateComponentBand(BaseModel):
    """Band parameters for tiered/banded rate calculations."""

    model_config = ConfigDict(extra="allow")

    supporting_text: str | None = Field(
        None, description="Supporting text for the rate band, if any."
    )
    band_low: float | None = Field(
        default=None, description="Lower bound of the rate band."
    )
    band_high: float | None = Field(
        default=None, description="Upper bound of the rate band."
    )
    band_uom: str | None = Field(
        default=None, description="Unit of measure for the rate band."
    )


class HtsRateComponent(BaseModel):
    """A single parsed duty rate component for an HTS code."""

    model_config = ConfigDict(extra="allow")

    htsno: str = Field(..., description="Original HTS code format (e.g. '7208.10.15').")
    hts_code: str = Field(..., description="Normalized HTS code.")
    rate_column: str = Field(..., description="One of general|special|other.")
    rate_basis: str = Field(
        ...,
        description="Rate basis: 'advalorem', 'specific', 'compound', 'free', etc.",
    )
    rate_usage: str | None = Field(
        default=None,
        description="How to apply: 'base', 'replace', 'additive', 'ignore'.",
    )
    rate_value: float | None = Field(
        default=None,
        description="Normalized rate (e.g. 0.05 for 5% or 2.5 for $2.50).",
    )
    uom: str | None = Field(
        default=None, description="Unit of measure key (e.g. 'kilogram')."
    )
    uom_extra: str | None = Field(default=None, description="Additional UOM context.")
    band_params: HtsRateComponentBand | None = Field(
        default=None, description="Band parameters for tiered rates."
    )
    component_text: str = Field(
        ..., description="Cleaned, chunk-level rate text (without program codes)."
    )
    base_text: str = Field(..., description="Full original rate text, cleaned.")
    lst_programs: list[str] = Field(
        default_factory=list, description="Applicable program codes."
    )
    lst_hts_refs: list[str] = Field(
        default_factory=list, description="Referenced HTS codes."
    )
    lst_footnotes_hts_refs: list[str] = Field(
        default_factory=list, description="Footnote HTS references."
    )
    lst_footnotes_text: list[str] = Field(
        default_factory=list, description="Footnote text content."
    )
    warning: str | None = Field(default=None, description="Parser warnings.")
    match_scenario: str | None = Field(
        default=None, description="Parsing scenario used."
    )
    conditions: list[SpecialRateCondition] | None = Field(
        default_factory=list, description="Special rate conditions."
    )


class HtsScheduleEntry(BaseModel):
    """An HTS schedule entry with code details, hierarchy, and rates."""

    model_config = ConfigDict(extra="allow")

    htsno: str = Field(
        ..., description="Original HTS code format (e.g. '7208.10.15.00')."
    )
    hts_code: str = Field(..., description="Normalized 10-digit HTS code.")
    description: str = Field(..., description="Description of the HTS code.")
    indent_level: int = Field(
        ..., description="Indentation level in the HTS hierarchy."
    )
    units_of_measures: list[str] | None = Field(
        default_factory=list, description="Statistical unit(s) of measure."
    )
    rate_components: list[HtsRateComponent] = Field(
        default_factory=list, description="Duty rate components."
    )
    footnotes: dict[str, list[dict[str, Any]]] = Field(
        default_factory=dict, description="Footnotes by type."
    )
    section_name: str | None = Field(default=None, description="HTS section name.")
    chapter_name: str | None = Field(default=None, description="HTS chapter name.")
    heading_name: str | None = Field(default=None, description="HTS heading name.")
    subheading_name: str | None = Field(
        default=None, description="HTS subheading name."
    )
    suffix_name: str | None = Field(default=None, description="HTS suffix name.")
    parent_hts_code: str | None = Field(
        default=None, description="Parent HTS code in hierarchy."
    )
