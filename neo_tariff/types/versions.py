"""HTS source version model.

Used by ``client.versions.list()``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class HtsSourceVersion(BaseModel):
    """Metadata for an available HTS revision."""

    model_config = ConfigDict(extra="allow")

    source_id: int | None = Field(default=None, description="Primary key.")
    year: int | None = Field(default=None, description="Tariff source year.")
    version: int | None = Field(default=None, description="Version/revision number.")
    release_date_unixts: float | None = Field(
        None, description="Release date as Unix timestamp."
    )
    release_effective_date_unixts: float | None = Field(
        None, description="Effective date as Unix timestamp."
    )
    release_notes: str | None = Field(None, description="Release notes.")
    import_unixts: float | None = Field(default=None, description="Import timestamp.")
    is_active: bool = Field(
        default=False, description="Whether revision is active in API responses."
    )
