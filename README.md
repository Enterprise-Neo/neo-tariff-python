# neo-tariff

Python SDK for the [Neo Tariff API](https://tariff-data.enterprise-neo.com) — US tariff duty calculation, HTS code search, and trade data.

[![PyPI version](https://img.shields.io/pypi/v/neo-tariff.svg)](https://pypi.org/project/neo-tariff/)
[![Python versions](https://img.shields.io/pypi/pyversions/neo-tariff.svg)](https://pypi.org/project/neo-tariff/)

## Installation

```bash
pip install neo-tariff
```

Or install a specific pre-release:

```bash
pip install neo-tariff --pre
```

## Release channels

- `main` channel: publishes stable builds to PyPI (`https://pypi.org/project/neo-tariff/`).
- `develop` channel: publishes `.dev` builds to TestPyPI
  (`https://test.pypi.org/project/neo-tariff/`), intended for integration with
  the develop TRD environment.

Maintainer runbook (sync + publishing pipeline):

- Internal `tariff-reference-data` repo: `docs/SDK_RELEASE_PROCESS.md`

Install from TestPyPI:

```bash
pip install --index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple neo-tariff --pre
```

## Quick start

```python
from neo_tariff import NeoTariff

# Zero-config: reads NEO_TARIFF_API_KEY (and optional base URL/retry settings)
client = NeoTariff()

result = client.rates.evaluate_entry(
    hts_code="7208.10.15",
    country_of_origin="CN",
    cost=10_000,
    qty=1_000,
)

data = result.data  # CalcResponse (typed Pydantic model)

if data.summary:
    net = data.summary.duty_totals.get("net")
    if net:
        print(f"Total duty: ${net.total:,.2f}")
```

## Authentication

The SDK auto-detects your API key from the `NEO_TARIFF_API_KEY` environment variable:

```bash
export NEO_TARIFF_API_KEY="ntf_..."
```

```python
from neo_tariff import NeoTariff

# Zero-config: reads NEO_TARIFF_API_KEY from environment
client = NeoTariff()

# Or pass explicitly (overrides env var)
client = NeoTariff(api_key="ntf_...")
```

The base URL can also be configured via environment variable for dev/staging:

```bash
export NEO_TARIFF_BASE_URL="https://staging.tariff-data.enterprise-neo.com"
```

You can also configure timeout/retry behavior with environment variables:

```bash
export NEO_TARIFF_TIMEOUT="30"        # seconds
export NEO_TARIFF_MAX_RETRIES="2"     # non-negative integer
```

If your project keeps credentials in a local `.env` file, load directly with:

```python
from neo_tariff import NeoTariff

client = NeoTariff.from_env_file(".env")
```

## Resources

### Rates — Tariff duty calculation

```python
# Single entry
result = client.rates.evaluate_entry(
    hts_code="7208.10.15",
    country_of_origin="CN",
    cost=10_000,
    qty=1_000,
    reciprocal=True,           # Include Ch.99 reciprocal tariffs
)
# result.data → CalcResponse

# Batch (up to 1000 entries)
result = client.rates.evaluate_entries(
    data=[
        {"hts_code": "7208.10.15", "country_of_origin": "CN", "cost": 10000, "qty": 1000},
        {"hts_code": "8471.30.01", "country_of_origin": "JP", "cost": 5000, "qty": 100},
    ]
)
# result.data → list[CalcResponse]

# Multi-country comparison for one HTS code
result = client.rates.evaluate_multicountry(
    hts_code="7208.10.15",
    countries=["CN", "DE", "JP"],
    cost=10_000,
    qty=1_000,
)
# result.data → list[CalcResponse]
```

### Search — HTS code lookup

```python
# Search by description
result = client.search.hts(query="steel plates", limit=10)
# result.data → list[APIRespSearchHtsItem]
for item in result.require_data():
    print(f"{item.hts_code}: {item.description}")

# Autocomplete by code prefix
result = client.search.autocomplete_hts(prefix="7208", limit=5)
# result.data → list[APIRespAutocompleteHtsItem]

# Natural language description search
result = client.search.hts_by_description(query="cold rolled steel sheets")
# result.data → list[APIRespAutocompleteHtsItem]

# Full-text document search (sections, chapters, codes, notes)
result = client.search.hts_docs(query="steel", limit=10)
# result.data → dict (untyped — complex nested structure)
```

### Context — HTS structure and country data

```python
# HTS code context with rates
result = client.context.get_hts_code("7208.10.15")
# result.data → APIRespDataHtsCodeHub

# Detailed code info
result = client.context.get_hts_details("7208100000")
# result.data → APIRespDataHtsCodeContext
print(result.data.description, result.data.indent_level)

# Batch HTS hub context
result = client.context.get_hts_hub_batch(["7208.10.15", "8471.30.01"])
# result.data → dict[str, Any]

# List HTS sections
result = client.context.list_sections()

# List chapters in a section
result = client.context.list_chapters_by_section("1")

# Country lookup
result = client.context.get_country("CN")
# result.data → CountryRecord
print(result.data.country_name, result.data.programs)

# Batch country lookup
result = client.context.get_countries_batch(["CN", "DE"])
# result.data → dict[str, CountryRecord]

# All countries
result = client.context.list_countries()
# result.data → list[CountryRecord]
```

### Compare — Version and country diffs

```python
# Compare tariff across countries
result = client.compare.tariff(
    hts_code="7208.10.15",
    countries=["CN", "DE"],
    cost=10_000,
    qty=1_000,
)
# result.data → dict[str, CalcResponse]

# Compare HTS rates between versions
result = client.compare.hts_rates(
    "7208.10.15",
    year_a=2025, version_a=15,
    year_b=2025, version_b=25,
)
# result.data → CompareRatesResponse

# Compare two source versions
result = client.compare.sources(
    year_a=2025, version_a=15,
    year_b=2025, version_b=25,
)
# result.data → CompareSourcesResponse
```

### Versions — Available HTS revisions

```python
result = client.versions.list()
# result.data → list[HtsSourceVersion]
for v in result.require_data():
    print(f"Year {v.year} v{v.version} {'(active)' if v.is_active else ''}")
```

## Async usage

Every resource method has an async counterpart:

```python
from neo_tariff import AsyncNeoTariff

async def main():
    async with AsyncNeoTariff(api_key="ntf_...") as client:
        result = await client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10_000,
            qty=1_000,
        )
        print(result.data.totals)
```

## Response envelope

All methods return `APIResponse[T]`:

```python
result = client.versions.list()
result.success   # bool
result.data      # T (the typed payload)
result.meta      # APIMeta | None (timestamp, operation, hts_year, etc.)
result.errors    # list[APIRespError] | None

# Convenience: raises NeoTariffError if data is None
data = result.require_data()
```

## Raw response access

For debugging or when you need the raw HTTP response:

```python
raw = client.with_raw_response.versions.list()
raw.http_response.status_code  # 200
raw.parsed                      # APIResponse or None
```

## Error handling

```python
from neo_tariff import (
    NeoTariffError,           # Base for all SDK errors
    NeoTariffHTTPError,       # Non-2xx HTTP response
    AuthenticationError,      # 401/403
    NotFoundError,            # 404
    ValidationError,          # 422
    RateLimitError,           # 429
    ServerError,              # 500+
    NeoTariffAPIError,        # 2xx but success=False
    NeoTariffConnectionError, # Network/timeout errors
)

try:
    result = client.rates.evaluate_entry(...)
except AuthenticationError:
    print("Check your API key")
except RateLimitError:
    print("Slow down!")
except NeoTariffHTTPError as e:
    print(f"HTTP {e.status_code}: {e.message}")
except NeoTariffAPIError as e:
    print(f"API error: {e.errors}")
except NeoTariffConnectionError:
    print("Network issue")
```

## Retry logic

The SDK automatically retries transient failures (408, 429, 500, 502, 503, 504 and network errors) with exponential backoff:

```python
client = NeoTariff(api_key="ntf_...", max_retries=2)   # Default: 2 retries
client = NeoTariff(api_key="ntf_...", max_retries=0)   # Disable retries
client = NeoTariff(api_key="ntf_...", max_retries=5)   # More retries for batch jobs
```

## Configuration

```python
client = NeoTariff(
    api_key="ntf_...",                                     # Or NEO_TARIFF_API_KEY env var
    base_url="https://tariff-data.enterprise-neo.com",     # Or NEO_TARIFF_BASE_URL env var
    timeout=30.0,                                           # Or NEO_TARIFF_TIMEOUT env var
    max_retries=2,                                          # Or NEO_TARIFF_MAX_RETRIES env var
)
```

| Environment variable | Description |
|---------------------|-------------|
| `NEO_TARIFF_API_KEY` | API key (used when `api_key=` not passed) |
| `NEO_TARIFF_BASE_URL` | API base URL (used when `base_url=` not passed) |
| `NEO_TARIFF_TIMEOUT` | Request timeout in seconds (used when `timeout=` not passed) |
| `NEO_TARIFF_MAX_RETRIES` | Retry count for transient failures (used when `max_retries=` not passed) |
| `NEO_TARIFF_LOG` | Set to `debug` to log HTTP requests/responses |

## Typed response models

All models use `ConfigDict(extra="allow")` — new API fields are preserved without breaking existing code.

| Method | Return type |
|--------|------------|
| `rates.evaluate_entry()` | `APIResponse[CalcResponse]` |
| `rates.evaluate_entries()` | `APIResponse[list[CalcResponse]]` |
| `rates.evaluate_multicountry()` | `APIResponse[list[CalcResponse]]` |
| `search.hts()` | `APIResponse[list[APIRespSearchHtsItem]]` |
| `search.autocomplete_hts()` | `APIResponse[list[APIRespAutocompleteHtsItem]]` |
| `search.hts_by_description()` | `APIResponse[list[APIRespAutocompleteHtsItem]]` |
| `search.hts_docs()` | `APIResponse[Any]` |
| `context.get_hts_code()` | `APIResponse[APIRespDataHtsCodeHub]` |
| `context.get_hts_details()` | `APIResponse[APIRespDataHtsCodeContext]` |
| `context.get_hts_hub()` | `APIResponse[Any]` |
| `context.get_hts_hub_batch()` | `APIResponse[dict[str, Any]]` |
| `context.get_hts_history()` | `APIResponse[Any]` |
| `context.get_document_index()` | `APIResponse[Any]` |
| `context.get_document()` | `APIResponse[Any]` |
| `context.list_sections()` | `APIResponse[Any]` |
| `context.list_chapters_by_section()` | `APIResponse[Any]` |
| `context.get_countries_batch()` | `APIResponse[dict[str, CountryRecord]]` |
| `context.list_countries()` | `APIResponse[list[CountryRecord]]` |
| `context.get_country()` | `APIResponse[CountryRecord]` |
| `compare.tariff()` | `APIResponse[dict[str, CalcResponse]]` |
| `compare.hts_rates()` | `APIResponse[CompareRatesResponse]` |
| `compare.sources()` | `APIResponse[CompareSourcesResponse]` |
| `versions.list()` | `APIResponse[list[HtsSourceVersion]]` |

## Request models (optional)

For IDE autocomplete on request bodies:

```python
from neo_tariff.types import CalcInputs

inputs = CalcInputs(
    hts_code="7208.10.15",
    country_of_origin="CN",
    cost=10_000,
    qty=1_000,
)
result = client.rates.evaluate_entry(**inputs.model_dump())
```

## Requirements

- Python >= 3.9
- [httpx](https://www.python-httpx.org/) >= 0.25
- [pydantic](https://docs.pydantic.dev/) >= 2.0

## Development

```bash
git clone https://github.com/Enterprise-Neo/neo-tariff-python.git
cd neo-tariff-python
pip install -e ".[dev]"

# Run tests
python -m pytest tests/ -q

# Lint
ruff check . --fix && ruff format .
```
