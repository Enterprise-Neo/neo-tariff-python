"""Models for tariff comparison responses.

Used by ``client.compare.hts_rates()`` and ``client.compare.sources()``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from neo_tariff.types.shared import HtsScheduleEntry


class CompareRatesResponse(BaseModel):
    """Comparison of HTS rates between two source versions.

    Used by ``GET /compare/hts/{hts_code}``.
    """

    model_config = ConfigDict(extra="allow")

    hts_code: str = Field(..., description="The HTS code being compared.")
    source_a: str = Field(..., description="First (baseline) HTS source identifier.")
    source_b: str = Field(..., description="Second HTS source identifier.")
    before_rates: HtsScheduleEntry | None = Field(
        default=None, description="Rate details from source_a."
    )
    after_rates: HtsScheduleEntry | None = Field(
        default=None, description="Rate details from source_b."
    )
    summary: str | None = Field(
        default=None, description="Human-readable summary of changes."
    )


class CompareSourcesResponse(BaseModel):
    """Comparison of two HTS source versions.

    Used by ``GET /compare/sources``.
    """

    model_config = ConfigDict(extra="allow")

    source_a: str = Field(..., description="First (baseline) HTS source identifier.")
    source_b: str = Field(..., description="Second HTS source identifier.")
    changes: dict[str, Any] = Field(
        default_factory=dict,
        description="Categorized changes (added, removed, modified).",
    )
    summary: str | None = Field(
        default=None, description="Human-readable summary of all changes."
    )
