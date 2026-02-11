"""Models for tariff rate calculation responses.

Used by ``client.rates.evaluate_entry()``, ``client.rates.evaluate_entries()``,
and ``client.rates.evaluate_multicountry()``.
"""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


# ---------------------------------------------------------------------------
# Response models — context blocks
# ---------------------------------------------------------------------------


class CalcInputsContextProgram(BaseModel):
    """Trade program metadata."""

    model_config = ConfigDict(extra="allow")

    code: str | None = Field(default=None, description="Program code.")
    name: str | None = Field(default=None, description="Full program name.")
    abbrev: str | None = Field(default=None, description="Abbreviation.")


class CalcInputsContextCountry(BaseModel):
    """Normalized country metadata derived from inputs."""

    model_config = ConfigDict(extra="allow")

    country_name: str | None = Field(default=None, description="Full country name.")
    official_name: str | None = Field(default=None, description="Official name.")
    common_name: str | None = Field(default=None, description="Common name.")
    country_code: str | None = Field(default=None, description="HTS country code.")
    iso_alpha2: str | None = Field(default=None, description="ISO alpha-2 code.")
    iso_alpha3: str | None = Field(default=None, description="ISO alpha-3 code.")
    programs: list[CalcInputsContextProgram] = Field(
        default_factory=list, description="Eligible trade programs."
    )
    sanction: str | None = Field(default=None, description="Sanction status.")


class CalcInputsContextDates(BaseModel):
    """Resolved dates derived from the request."""

    model_config = ConfigDict(extra="allow")

    import_date_resolved: str | None = Field(
        default=None, description="Resolved import date (YYYY-MM-DD)."
    )
    loading_date_resolved: str | None = Field(
        default=None, description="Resolved loading date (YYYY-MM-DD)."
    )


class CalcInputsContextHtsRevision(BaseModel):
    """Resolved HTS revision metadata."""

    model_config = ConfigDict(extra="allow")

    hts_year: int | None = Field(default=None, description="HTS revision year.")
    hts_version: int | None = Field(default=None, description="HTS version.")
    source_id: int | None = Field(default=None, description="Database source ID.")


class CalcInputsContextVersionSelection(BaseModel):
    """Details about which HTS version was selected and how."""

    model_config = ConfigDict(extra="allow")

    source_id: int | None = Field(default=None, description="Database primary key.")
    year: int | None = Field(default=None, description="HTS schedule year.")
    version: int | None = Field(
        default=None, description="HTS version/revision number."
    )
    effective_start: str | None = Field(
        default=None, description="Effective date (YYYY-MM-DD)."
    )
    release_date: str | None = Field(
        default=None, description="Publication date (YYYY-MM-DD)."
    )
    selection_method: str | None = Field(
        default=None, description="Method used to select this version."
    )
    warnings: list[str] = Field(default_factory=list, description="Selection warnings.")


class CalcInputsContextDateResolution(BaseModel):
    """How dates were resolved for the calculation."""

    model_config = ConfigDict(extra="allow")

    import_date_provided: str | None = Field(
        default=None, description="Import date from request."
    )
    import_date_used: str | None = Field(
        default=None, description="Import date actually used."
    )
    loading_date_provided: str | None = Field(
        default=None, description="Loading date from request."
    )
    loading_date_used: str | None = Field(
        default=None, description="Loading date used."
    )
    defaulting_source: str | None = Field(
        default=None, description="How import_date was derived."
    )
    conflicts: list[str] = Field(
        default_factory=list, description="Detected date conflicts."
    )


class CalcInputsContext(BaseModel):
    """Derived metadata from the calculation inputs."""

    model_config = ConfigDict(extra="allow")

    country: CalcInputsContextCountry | None = Field(
        default=None, description="Country metadata."
    )
    dates: CalcInputsContextDates | None = Field(
        default=None, description="Resolved dates."
    )
    hts_revision: CalcInputsContextHtsRevision | None = Field(
        default=None, description="HTS revision metadata."
    )
    version_selection: CalcInputsContextVersionSelection | None = Field(
        default=None, description="Version selection details."
    )
    date_resolution: CalcInputsContextDateResolution | None = Field(
        default=None, description="Date resolution details."
    )


# ---------------------------------------------------------------------------
# Response models — duty calculation
# ---------------------------------------------------------------------------


class CalcDutyTotals(BaseModel):
    """Aggregated duty amounts for a given scope."""

    model_config = ConfigDict(extra="allow")

    ad_valorem: float = Field(default=0.0, description="Ad valorem duty in USD.")
    specific: float = Field(default=0.0, description="Specific duty in USD.")
    total: float = Field(default=0.0, description="Combined total duty in USD.")


class CalcBaseComponent(BaseModel):
    """A single duty component in the calculation."""

    model_config = ConfigDict(extra="allow")

    hts_code: str = Field(..., description="HTS code this component applies to.")
    listed_hts_code: str | None = Field(
        default=None, description="HTS code where rate is actually listed."
    )
    rate_column: str = Field(..., description="Rate column.")
    rate_usage: str = Field(..., description="How rate is applied.")
    rate_basis: str = Field(..., description="Rate type.")
    rate_value: float | None = Field(default=None, description="Numeric rate.")
    uom: str | None = Field(default=None, description="Unit of measure.")
    uom_extra: str | None = Field(default=None, description="Secondary UOM.")
    duty_advalorem: float = Field(default=0.0, description="Ad valorem duty in USD.")
    duty_specific: float = Field(default=0.0, description="Specific duty in USD.")
    duty_total: float = Field(default=0.0, description="Total duty in USD.")
    description: str | None = Field(default=None, description="Description.")
    listed_rate_text: str | None = Field(
        default=None, description="Original rate text."
    )
    programs: list[str] = Field(
        default_factory=list, description="Applicable trade programs."
    )


class CalcRuleReferences(BaseModel):
    """Cross-references supporting a rule selection."""

    model_config = ConfigDict(extra="allow")

    hts_refs: list[str] = Field(default_factory=list, description="HTS references.")
    footnotes_hts_refs: list[str] = Field(
        default_factory=list, description="Footnote HTS references."
    )
    footnotes_text: list[str] = Field(
        default_factory=list, description="Footnote text."
    )


class CalcRuleItem(BaseModel):
    """A single applied base or reciprocal rule."""

    model_config = ConfigDict(extra="allow")

    type: str = Field(..., description="Rule type (base or reciprocal).")
    code: str = Field(..., description="HTS or Chapter 99 provision code.")
    id: str | None = Field(default=None, description="Rule instance identifier.")
    breakdown_ref: str | None = Field(
        default=None, description="Reference to breakdown array."
    )
    rate_column: str | None = Field(default=None, description="Rate column.")
    rate_basis: str | None = Field(default=None, description="Rate basis.")
    rate_value: float | None = Field(default=None, description="Rate value.")
    computed_amount: float | None = Field(
        default=None, description="Computed duty in USD."
    )
    description: str | None = Field(default=None, description="Rule description.")
    source: str | None = Field(default=None, description="Rule source (e.g., 'IEEPA').")
    references: CalcRuleReferences | None = Field(
        default=None, description="Cross-references."
    )
    related_99_codes: list[str] = Field(
        default_factory=list, description="Related Chapter 99 codes."
    )
    applies: bool | None = Field(default=None, description="Whether rule applies.")
    calculation_method: str | None = Field(
        default=None, description="Calculation method used."
    )


class CalcRulesView(BaseModel):
    """Unified view of all applied base and reciprocal rules."""

    model_config = ConfigDict(extra="allow")

    base: list[CalcRuleItem] = Field(
        default_factory=list, description="Base tariff rules."
    )
    reciprocal: list[CalcRuleItem] = Field(
        default_factory=list, description="Chapter 99 reciprocal rules."
    )


class ComponentLine(BaseModel):
    """A material-specific evaluation line."""

    model_config = ConfigDict(extra="allow")

    line_number: int = Field(description="Sequential line number.")
    line_name: str | None = Field(
        default=None, description="Material type or null for simple scenarios."
    )
    line_value: float = Field(description="Value for this material portion.")
    line_percent: float = Field(description="Percentage of total value (0-100).")
    line_country: str | None = Field(
        default=None, description="Country used for this line evaluation."
    )
    line_total_duty: float = Field(default=0.0, description="Total duty for this line.")
    rules: list[CalcBaseComponent] = Field(
        default_factory=list, description="Duty components for this line."
    )


# ---------------------------------------------------------------------------
# Response models — V3 summary and breakdown
# ---------------------------------------------------------------------------


class V3DutyTotals(BaseModel):
    """Duty totals grouped by axis."""

    model_config = ConfigDict(extra="allow")

    percent_based: float = Field(default=0.0, description="Ad valorem duties in USD.")
    unit_based: float = Field(default=0.0, description="Specific duties in USD.")
    total: float = Field(default=0.0, description="Combined total in USD.")


class V3EffectiveRates(BaseModel):
    """Effective duty rates grouped by axis."""

    model_config = ConfigDict(extra="allow")

    percent_based: float = Field(default=0.0, description="Effective ad valorem rate.")
    unit_based: float = Field(default=0.0, description="Effective specific rate.")
    total: float = Field(default=0.0, description="Combined effective rate.")


class V3ValuationBasis(BaseModel):
    """Declared value basis used for calculations."""

    model_config = ConfigDict(extra="allow")

    label: str = Field(default="declared_value", description="Valuation basis type.")
    amount: float | None = Field(default=None, description="Valuation amount.")
    currency: str | None = Field(default=None, description="Currency code.")
    notes: list[str] = Field(default_factory=list, description="Notes.")


class V3CargoValue(BaseModel):
    """Cargo value echo in the V3 summary."""

    model_config = ConfigDict(extra="allow")

    amount: float | None = Field(default=None, description="Cargo value amount.")
    currency: str | None = Field(default=None, description="Currency code.")
    quantity: float | None = Field(default=None, description="Quantity.")
    qty_uom: str | None = Field(default=None, description="Quantity UOM.")


class V3Flags(BaseModel):
    """Calculation characteristic flags."""

    model_config = ConfigDict(extra="allow")

    has_reciprocal: bool = Field(
        default=False, description="Whether reciprocal duties apply."
    )
    has_quota: bool = Field(default=False, description="Whether quotas apply.")
    calculation_methods: list[str] = Field(
        default_factory=list, description="Methods used."
    )


class V3ListedRateCap(BaseModel):
    """Optional cap metadata for listed rates."""

    model_config = ConfigDict(extra="allow")

    kind: str | None = Field(default=None, description="Cap type.")
    value: float | None = Field(default=None, description="Cap value.")
    uom: str | None = Field(default=None, description="Cap UOM.")


class V3ListedRate(BaseModel):
    """Listed rate details in breakdown charges."""

    model_config = ConfigDict(extra="allow")

    value: float | None = Field(default=None, description="Numeric rate value.")
    display: str | None = Field(
        default=None, description="Display string (e.g., '25%')."
    )
    uom: str | None = Field(default=None, description="UOM for specific rates.")
    cap: V3ListedRateCap | None = Field(default=None, description="Rate cap.")
    notes: list[str] = Field(default_factory=list, description="Rate notes.")


class V3Coverage(BaseModel):
    """Coverage metadata for a breakdown charge."""

    model_config = ConfigDict(extra="allow")

    quantity: float | None = Field(default=None, description="Quantity covered.")
    uom: str | None = Field(default=None, description="Unit of measure.")
    value_used: float | None = Field(
        default=None, description="Value used for calculation."
    )
    derived_qty: float | None = Field(default=None, description="Derived quantity.")
    derived_uom: str | None = Field(default=None, description="Derived UOM.")


class V3BreakdownCharge(BaseModel):
    """A single charge entry within a breakdown row."""

    model_config = ConfigDict(extra="allow")

    type: str = Field(..., description="Charge type (percent_based or unit_based).")
    listed_rate: V3ListedRate | None = Field(
        default=None, description="Listed rate details."
    )
    applied_rate: float | None = Field(
        default=None, description="Rate actually applied."
    )
    per_unit_rate: float | None = Field(default=None, description="Per-unit rate.")
    computed_amount: float | None = Field(
        default=None, description="Computed duty in USD."
    )
    coverage: V3Coverage | None = Field(default=None, description="Coverage metadata.")


class V3Condition(BaseModel):
    """Condition or note on a breakdown row."""

    model_config = ConfigDict(extra="allow")

    tag: str = Field(..., description="Condition tag/identifier.")
    detail: str | None = Field(default=None, description="Detail text.")


class V3BreakdownItem(BaseModel):
    """A structured breakdown row (base, reciprocal, or total)."""

    model_config = ConfigDict(extra="allow")

    id: str | None = Field(default=None, description="Unique identifier.")
    line_seq: int | None = Field(default=None, description="Sequence number.")
    kind: str | None = Field(default=None, description="Item type.")
    source_ref: dict[str, Any] | None = Field(
        default=None, description="Source rule/rate reference."
    )
    description: str | None = Field(default=None, description="Description.")
    charges: list[V3BreakdownCharge] = Field(
        default_factory=list, description="Charges."
    )
    totals: V3DutyTotals | None = Field(
        default=None, description="Totals for this item."
    )
    percent_of_cost: float | None = Field(
        default=None, description="Duty as percentage of cargo value."
    )
    programs: list[str] = Field(default_factory=list, description="Trade programs.")
    conditions: list[V3Condition] = Field(
        default_factory=list, description="Conditions."
    )
    applies: bool = Field(default=True, description="Whether item applies.")
    non_application_reason: str | None = Field(
        default=None, description="Reason if not applicable."
    )


class V3Summary(BaseModel):
    """Top-level V3 summary block."""

    model_config = ConfigDict(extra="allow")

    currency_code: str | None = Field(default=None, description="Currency code.")
    cargo_value: V3CargoValue | None = Field(default=None, description="Cargo value.")
    duty_totals: dict[str, V3DutyTotals] | None = Field(
        default=None, description="Duty totals by category."
    )
    effective_rates: dict[str, V3EffectiveRates] | None = Field(
        default=None, description="Effective rates by category."
    )
    valuation_basis: V3ValuationBasis | None = Field(
        default=None, description="Valuation basis used."
    )
    flags: V3Flags | None = Field(default=None, description="Calculation flags.")


# ---------------------------------------------------------------------------
# Response models — reciprocal tariffs
# ---------------------------------------------------------------------------


class ReciprocalContext(BaseModel):
    """Input context used for reciprocal rate evaluation."""

    model_config = ConfigDict(extra="allow")

    hts_code: str | None = Field(default=None, description="HTS code evaluated.")
    country_of_origin: str | None = Field(
        default=None, description="Country (ISO alpha-2)."
    )
    import_date: str | None = Field(default=None, description="Import date.")
    loading_date: str | None = Field(default=None, description="Loading date.")
    resolved_import_date: str | None = Field(
        default=None, description="Resolved import date."
    )
    resolved_loading_date: str | None = Field(
        default=None, description="Resolved loading date."
    )
    defaulting_notes: list[str] = Field(
        default_factory=list, description="Date defaulting notes."
    )
    value: float | None = Field(default=None, description="Customs value.")
    quantity: float | None = Field(default=None, description="Quantity.")
    rate_column: str | None = Field(default=None, description="Rate column used.")
    base_ad_valorem_rate: float | None = Field(
        default=None, description="Base ad valorem rate."
    )
    base_specific_rate: float | None = Field(
        default=None, description="Base specific rate."
    )
    admitted_to_ftz: bool = Field(default=False, description="Admitted to FTZ.")
    is_donation: bool = Field(default=False, description="Humanitarian donation.")
    is_informational: bool = Field(
        default=False, description="Informational materials."
    )
    is_personal_baggage: bool = Field(default=False, description="Personal baggage.")
    usmca_claim: bool = Field(default=False, description="USMCA claim.")
    program_qualified: bool = Field(default=True, description="Program eligibility.")
    chapter98_provision: str | None = Field(
        default=None, description="Chapter 98 provision."
    )
    materials: list[dict[str, Any]] | None = Field(
        default=None, description="Material composition."
    )


class AiEvaluationResponse(BaseModel):
    """AI assessment of conditional exemption applicability."""

    model_config = ConfigDict(extra="allow")

    confidence: int | None = Field(default=None, description="Confidence score 1-10.")
    recommendation: str | None = Field(
        default=None, description="One of 'likely', 'unlikely', or 'uncertain'."
    )
    reasoning: str | None = Field(default=None, description="One-sentence explanation.")


class ConditionalExemptionResponse(BaseModel):
    """A conditional exemption that may apply based on product characteristics."""

    model_config = ConfigDict(extra="allow")

    rule_code: str | None = Field(
        default=None, description="Chapter 99 code (e.g., '9903.02.78')."
    )
    is_selected: bool = Field(
        default=False, description="User confirmed this exemption."
    )
    note_unique_id: str = Field(default="", description="Source note unique ID.")
    note_text: str | None = Field(
        default=None, description="Note describing the conditional requirement."
    )
    matched_hts_pattern: str | None = Field(
        default=None, description="HTS pattern from the note that matched."
    )
    would_exclude: list[str] = Field(
        default_factory=list, description="Rules excluded if confirmed."
    )
    ai_evaluation: AiEvaluationResponse | None = Field(
        default=None, description="AI assessment (when product_usage provided)."
    )


class ReciprocalRule(BaseModel):
    """A reciprocal rate rule from Chapter 99."""

    model_config = ConfigDict(extra="allow")

    rule_code: str | None = Field(default=None, description="Chapter 99 rule code.")
    description: str | None = Field(default=None, description="Rule description.")
    related_99_codes: list[str] = Field(
        default_factory=list, description="Related Chapter 99 codes."
    )
    additional_duty_rate: float | None = Field(
        default=None, description="Additional duty rate (0.25 = 25%)."
    )
    computed_rate: float | None = Field(
        default=None, description="Computed effective rate."
    )
    computed_amount: float | None = Field(
        default=None, description="Computed duty in USD."
    )
    applies: bool = Field(default=False, description="Whether rule applies.")


class ReciprocalTotals(BaseModel):
    """Aggregated reciprocal duty results."""

    model_config = ConfigDict(extra="allow")

    additional_rate: float = Field(default=0.0, description="Total additional rate.")
    additional_duty_amount: float = Field(
        default=0.0, description="Total additional duty in USD."
    )


class ReciprocalResponse(BaseModel):
    """Reciprocal tariff evaluation results (Chapter 99)."""

    model_config = ConfigDict(extra="allow")

    error: str | None = Field(default=None, description="Error if evaluation failed.")
    context: ReciprocalContext | None = Field(
        default=None, description="Input context."
    )
    totals: ReciprocalTotals | None = Field(
        default=None, description="Aggregated totals."
    )
    rules: list[ReciprocalRule] = Field(
        default_factory=list, description="Evaluated rules."
    )
    conditional_exemptions: list[ConditionalExemptionResponse] = Field(
        default_factory=list,
        description="Conditional exemptions that may apply.",
    )


# ---------------------------------------------------------------------------
# Top-level calculation response
# ---------------------------------------------------------------------------


class CalcResponse(BaseModel):
    """Complete tariff calculation response.

    Contains the full calculation result including inputs echo,
    derived context, duty totals, component breakdown, reciprocal
    evaluation, and V3 summary/breakdown.
    """

    model_config = ConfigDict(extra="allow")

    # inputs is a dict here (not CalcInputs) to avoid request-model dependency.
    # The server echoes back the input parameters as-is.
    inputs: dict[str, Any] | None = Field(
        default=None, description="Echo of input parameters."
    )
    inputs_context: CalcInputsContext | None = Field(
        default=None, description="Derived context."
    )
    totals: dict[str, CalcDutyTotals] = Field(
        default_factory=dict, description="Duty totals by category."
    )
    components: list[ComponentLine] = Field(
        default_factory=list, description="Material line components."
    )
    is_composite: bool = Field(
        default=False, description="Multiple material lines exist."
    )
    reciprocal: ReciprocalResponse | None = Field(
        default=None, description="Chapter 99 evaluation results."
    )
    conditional_exemptions: list[ConditionalExemptionResponse] = Field(
        default_factory=list, description="Conditional exemptions."
    )
    rules: CalcRulesView | None = Field(default=None, description="Unified rules view.")
    schema_version: str | None = Field(
        default=None, description="Response schema version."
    )
    summary: V3Summary | None = Field(default=None, description="V3 summary block.")
    breakdown: list[V3BreakdownItem] | None = Field(
        default=None, description="V3 detailed breakdown."
    )
    adjustment_metadata: dict[str, Any] | None = Field(
        default=None, description="Rate adjustment details."
    )
    error_message: str | None = Field(
        default=None, description="Error message if calculation failed."
    )
