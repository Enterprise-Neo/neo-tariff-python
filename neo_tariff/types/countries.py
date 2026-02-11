"""Country record model.

Used by ``client.context.list_countries()`` and ``client.context.get_country()``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class CountryRecord(BaseModel):
    """A country with trade program eligibility and sanctions info."""

    model_config = ConfigDict(extra="allow")

    country_name: str = Field(..., description="ISO 3166 short name.")
    official_name: str | None = Field(default=None, description="Formal country name.")
    common_name: str | None = Field(default=None, description="Common country name.")
    country_code: str | None = Field(default=None, description="Numeric ISO 3166 code.")
    iso_alpha2: str | None = Field(default=None, description="Alpha-2 code.")
    iso_alpha3: str | None = Field(default=None, description="Alpha-3 code.")
    programs: list[str] = Field(
        default_factory=list, description="Eligible trade programs."
    )
    sanction: str | None = Field(None, description="Sanction type, if any.")
    aliases: list[str] = Field(
        default_factory=list, description="All normalized identifiers."
    )
