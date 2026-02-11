"""neo-tariff – Python SDK for the Neo Tariff API."""

from neo_tariff._types import APIMeta, APIPagination, APIRespError, APIResponse
from neo_tariff._version import __version__
from neo_tariff.async_client import AsyncNeoTariff
from neo_tariff.client import NeoTariff
from neo_tariff.exceptions import (
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    NeoTariffAPIError,
    NeoTariffConnectionError,
    NeoTariffHTTPError,
    NeoTariffError,
    ValidationError,
)
from neo_tariff.types.compare import CompareRatesResponse, CompareSourcesResponse
from neo_tariff.types.context import APIRespDataHtsCodeContext, APIRespDataHtsCodeHub
from neo_tariff.types.countries import CountryRecord
from neo_tariff.types.rates import CalcResponse
from neo_tariff.types.search import APIRespAutocompleteHtsItem, APIRespSearchHtsItem
from neo_tariff.types.versions import HtsSourceVersion

__all__ = [
    "__version__",
    "NeoTariff",
    "AsyncNeoTariff",
    "APIResponse",
    "APIMeta",
    "APIPagination",
    "APIRespError",
    "NeoTariffError",
    "NeoTariffHTTPError",
    "NeoTariffAPIError",
    "NeoTariffConnectionError",
    "AuthenticationError",
    "NotFoundError",
    "ValidationError",
    "RateLimitError",
    "ServerError",
    # Response types
    "CalcResponse",
    "CompareRatesResponse",
    "CompareSourcesResponse",
    "APIRespSearchHtsItem",
    "APIRespAutocompleteHtsItem",
    "APIRespDataHtsCodeHub",
    "APIRespDataHtsCodeContext",
    "HtsSourceVersion",
    "CountryRecord",
]
