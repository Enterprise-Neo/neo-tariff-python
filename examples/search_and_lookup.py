"""Search and context lookup example.

Demonstrates HTS search, autocomplete, and context lookups.
All methods return typed Pydantic models for IDE autocomplete.

Usage:
    export NEO_TARIFF_API_KEY="ntf_your_key_here"
    python examples/search_and_lookup.py
"""

import os

from neo_tariff import NeoTariff

api_key = os.environ.get("NEO_TARIFF_API_KEY", "")
if not api_key:
    raise SystemExit("Set NEO_TARIFF_API_KEY environment variable first.")

with NeoTariff(api_key=api_key) as client:
    # --- Search by description (typed: list[APIRespSearchHtsItem]) ---
    print("=== Search: 'steel pipes' ===")
    search = client.search.hts(query="steel pipes", limit=3)
    for item in search.require_data():
        print(f"  {item.hts_code}: {item.description[:60]}...")

    # --- Autocomplete by code prefix (typed: list[APIRespAutocompleteHtsItem]) ---
    print("\n=== Autocomplete: '7208' ===")
    auto = client.search.autocomplete_hts(prefix="7208", limit=5)
    for item in auto.require_data():
        print(f"  {item.htsno}: {item.description[:60]}...")

    # --- Context: HTS code details (typed: APIRespDataHtsCodeContext) ---
    print("\n=== Context details: 7208100000 ===")
    details = client.context.get_hts_details("7208100000")
    d = details.require_data()
    print(f"  Description: {d.description}")
    print(f"  Indent level: {d.indent_level}")

    # --- Country lookup (typed: CountryRecord) ---
    print("\n=== Country: CN ===")
    country = client.context.get_country("CN")
    c = country.require_data()
    print(f"  Name: {c.country_name}")
    print(f"  Programs: {', '.join(c.programs)}")

    # --- List available HTS versions (typed: list[HtsSourceVersion]) ---
    print("\n=== HTS Versions ===")
    versions = client.versions.list()
    for v in versions.require_data():
        active = " (active)" if v.is_active else ""
        print(f"  Year {v.year} v{v.version}{active}")
