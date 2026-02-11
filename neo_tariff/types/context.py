"""Models for HTS context responses.

Used by ``client.context.get_hts_code()`` and ``client.context.get_hts_details()``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from neo_tariff.types.shared import HtsRateComponent, HtsScheduleEntry


class APIRespDataHtsCodeContext(BaseModel):
    """Detailed context for a single HTS code including hierarchy and rates.

    Used by ``GET /context/hts/{hts_code}/details``.
    """

    model_config = ConfigDict(extra="allow")

    hts_code: str = Field(..., description="Normalized 10-digit HTS code.")
    htsno: str | None = Field(default=None, description="Dotted HTS format.")
    description: str = Field(..., description="Full description.")
    indent_level: int = Field(..., description="Hierarchy indent level (0-5).")
    units_of_measures: list[str] | None = Field(
        default=None, description="Statistical unit(s) of measure."
    )
    parent_hts_code: str | None = Field(default=None, description="Parent HTS code.")
    section_name: str | None = Field(default=None, description="Section name.")
    chapter_name: str | None = Field(default=None, description="Chapter name.")
    heading_name: str | None = Field(default=None, description="Heading name.")
    subheading_name: str | None = Field(default=None, description="Subheading name.")
    suffix_name: str | None = Field(default=None, description="Suffix name.")
    footnotes: dict[str, Any] | None = Field(
        default=None, description="Footnotes by type."
    )
    rates: list[HtsRateComponent] | None = Field(
        default_factory=list, description="Duty rate components."
    )


class APIRespDataHtsCodeHub(BaseModel):
    """HTS code context with details, rates, and optional reciprocal evaluation.

    Used by ``GET /context/hts/{hts_code}``.
    """

    model_config = ConfigDict(extra="allow")

    details: HtsScheduleEntry | None = Field(
        default=None, description="HTS code details with hierarchy."
    )
    rates: list[HtsRateComponent] = Field(
        default_factory=list, description="Duty rate components."
    )
    reciprocal: dict[str, Any] | None = Field(
        default=None,
        description="Chapter 99 reciprocal evaluation (when reciprocal=true).",
    )
