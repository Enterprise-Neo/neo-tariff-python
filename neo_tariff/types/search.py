"""Models for HTS search responses.

Used by ``client.search.hts()``, ``client.search.autocomplete_hts()``,
and ``client.search.hts_by_description()``.
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, Field


class APIRespSearchHtsItem(BaseModel):
    """A single HTS search result."""

    model_config = ConfigDict(extra="allow")

    type: str = Field(default="hts", description="Result type.")
    hts_code: str = Field(..., description="Matched HTS code.")
    description: str = Field(..., description="Code description.")
    score: float | None = Field(default=None, description="Match score.")
    section_name: str | None = Field(default=None, description="Section name.")
    chapter_name: str | None = Field(default=None, description="Chapter name.")
    lst_footnotes_text: list[str] | None = Field(
        default=None, description="Footnotes (when include_notes=True)."
    )


class APIRespAutocompleteHtsItem(BaseModel):
    """A single HTS autocomplete/description-search result."""

    model_config = ConfigDict(extra="allow")

    hts_code: str = Field(..., description="Normalized 10-digit HTS code.")
    htsno: str = Field(..., description="Dotted HTS format.")
    description: str = Field(..., description="Full description.")
    digit_length: int = Field(..., description="Effective digit length.")
    section_name: str | None = Field(default=None, description="Section name.")
    chapter_name: str | None = Field(default=None, description="Chapter name.")
    heading_name: str | None = Field(default=None, description="Heading name.")
    subheading_name: str | None = Field(default=None, description="Subheading name.")
    suffix_name: str | None = Field(default=None, description="Suffix name.")
    units_of_measures: list[str] | None = Field(
        default_factory=list, description="Units of measure."
    )
    indent_level: int | None = Field(
        default=None, description="Hierarchy indent level."
    )
    parent_hts_code: str | None = Field(default=None, description="Parent HTS code.")
    score: float | None = Field(default=None, description="Relevance score.")
