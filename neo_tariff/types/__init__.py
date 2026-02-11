"""Typed request and response models for the Tariff SDK."""

from neo_tariff.types.context import (
    APIRespDataHtsCodeContext,
    APIRespDataHtsCodeHub,
)
from neo_tariff.types.countries import CountryRecord
from neo_tariff.types.rates import (
    AiEvaluationResponse,
    CalcBaseComponent,
    CalcDutyTotals,
    CalcInputsContext,
    CalcInputsContextCountry,
    CalcInputsContextDateResolution,
    CalcInputsContextDates,
    CalcInputsContextHtsRevision,
    CalcInputsContextProgram,
    CalcInputsContextVersionSelection,
    CalcResponse,
    CalcRuleItem,
    CalcRuleReferences,
    CalcRulesView,
    ComponentLine,
    ConditionalExemptionResponse,
    ReciprocalContext,
    ReciprocalResponse,
    ReciprocalRule,
    ReciprocalTotals,
    V3BreakdownCharge,
    V3BreakdownItem,
    V3CargoValue,
    V3Condition,
    V3Coverage,
    V3DutyTotals,
    V3EffectiveRates,
    V3Flags,
    V3ListedRate,
    V3ListedRateCap,
    V3Summary,
    V3ValuationBasis,
)
from neo_tariff.types.search import (
    APIRespAutocompleteHtsItem,
    APIRespSearchHtsItem,
)
from neo_tariff.types.shared import (
    HtsRateComponent,
    HtsRateComponentBand,
    HtsScheduleEntry,
    MaterialType,
    RateBasis,
    RateColumn,
    RateUsage,
    SpecialRateCondition,
)
from neo_tariff.types.compare import (
    CompareRatesResponse,
    CompareSourcesResponse,
)
from neo_tariff.types.requests import (
    CalcBatchInputs,
    CalcInputs,
    MaterialComponent,
    MaterialProcessAluminum,
    MaterialProcessSteel,
)
from neo_tariff.types.versions import HtsSourceVersion

__all__ = [
    # Rates
    "CalcResponse",
    "CalcInputsContext",
    "CalcInputsContextProgram",
    "CalcInputsContextCountry",
    "CalcInputsContextDates",
    "CalcInputsContextHtsRevision",
    "CalcInputsContextVersionSelection",
    "CalcInputsContextDateResolution",
    "CalcDutyTotals",
    "CalcBaseComponent",
    "CalcRuleReferences",
    "CalcRuleItem",
    "CalcRulesView",
    "ComponentLine",
    # V3
    "V3Summary",
    "V3BreakdownItem",
    "V3BreakdownCharge",
    "V3DutyTotals",
    "V3EffectiveRates",
    "V3ValuationBasis",
    "V3CargoValue",
    "V3Flags",
    "V3ListedRate",
    "V3ListedRateCap",
    "V3Coverage",
    "V3Condition",
    # Reciprocal
    "ReciprocalResponse",
    "ReciprocalRule",
    "ReciprocalTotals",
    "ReciprocalContext",
    "ConditionalExemptionResponse",
    "AiEvaluationResponse",
    # Search
    "APIRespSearchHtsItem",
    "APIRespAutocompleteHtsItem",
    # Context
    "APIRespDataHtsCodeContext",
    "APIRespDataHtsCodeHub",
    # Countries
    "CountryRecord",
    # Versions
    "HtsSourceVersion",
    # Compare
    "CompareRatesResponse",
    "CompareSourcesResponse",
    # Shared
    "HtsRateComponent",
    "HtsRateComponentBand",
    "HtsScheduleEntry",
    "SpecialRateCondition",
    "RateColumn",
    "RateBasis",
    "RateUsage",
    "MaterialType",
    # Request models
    "CalcInputs",
    "CalcBatchInputs",
    "MaterialComponent",
    "MaterialProcessSteel",
    "MaterialProcessAluminum",
]
