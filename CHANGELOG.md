# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-02-11

### Added

- Initial release of the Neo Tariff Python SDK.
- Sync (`NeoTariff`) and async (`AsyncNeoTariff`) clients.
- **Rates resource**: `evaluate_entry()`, `evaluate_entries()`, `evaluate_multicountry()`.
- **Search resource**: `hts()`, `hts_docs()`, `autocomplete_hts()`, `hts_by_description()`.
- **Context resource**: `list_sections()`, `list_chapters_by_section()`, `get_hts_code()`, `get_hts_details()`, `get_hts_hub()`, `list_countries()`, `get_country()`.
- **Compare resource**: `tariff()`, `hts_rates()`, `sources()`.
- **Versions resource**: `list()`.
- Typed response models using Pydantic v2 (`CalcResponse`, `APIRespSearchHtsItem`, `APIRespAutocompleteHtsItem`, `APIRespDataHtsCodeHub`, `APIRespDataHtsCodeContext`, `CountryRecord`, `HtsSourceVersion`, `CompareRatesResponse`, `CompareSourcesResponse`).
- `APIResponse[T]` envelope with typed `data`, `meta`, and `errors`.
- `with_raw_response` escape hatch for raw HTTP access.
- Automatic retry with exponential backoff for transient failures.
- Structured exception hierarchy: `AuthenticationError`, `NotFoundError`, `ValidationError`, `RateLimitError`, `ServerError`, `NeoTariffAPIError`, `NeoTariffConnectionError`.
- Optional typed request models (`CalcInputs`, `CalcBatchInputs`).
- Forward-compatible models with `extra="allow"`.
