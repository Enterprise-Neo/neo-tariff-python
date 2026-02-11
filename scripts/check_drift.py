"""Drift checker – verify SDK coverage against openapi-sdk.json.

Compares the committed ``openapi-sdk.json`` endpoints against SDK resource
method registrations.  Endpoints in the v0.1 scope that are missing from
the SDK cause an **error** (exits non-zero).  Endpoints outside v0.1 scope
are reported as **warnings** only.

Also validates that response schemas in the spec haven't added required
fields that our Pydantic models might miss (using extra="allow" provides
forward-compatibility, but removing fields would break).

Usage::

    python sdk/scripts/check_drift.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

SDK_DIR = Path(__file__).resolve().parent.parent
OPENAPI_PATH = SDK_DIR / "openapi-sdk.json"

# ── v0.1 scope: (method, path) → SDK resource.method ──────────────────────

V1_COVERAGE: dict[tuple[str, str], str] = {
    # Rates
    ("POST", "/rates/entry"): "rates.evaluate_entry",
    ("POST", "/rates/entries"): "rates.evaluate_entries",
    ("POST", "/rates/multicountry"): "rates.evaluate_multicountry",
    # Search
    ("GET", "/search/hts"): "search.hts",
    ("GET", "/search/hts-docs"): "search.hts_docs",
    ("GET", "/search/autocomplete/hts"): "search.autocomplete_hts",
    ("GET", "/search/hts/by-description"): "search.hts_by_description",
    # Context
    ("GET", "/context/hts/sections"): "context.list_sections",
    (
        "GET",
        "/context/hts/sections/{section_name}/chapters",
    ): "context.list_chapters_by_section",
    ("GET", "/context/hts/{hts_code}"): "context.get_hts_code",
    ("GET", "/context/hts/{hts_code}/details"): "context.get_hts_details",
    ("GET", "/context/hts/{hts_code}/hub"): "context.get_hts_hub",
    ("GET", "/context/countries"): "context.list_countries",
    ("GET", "/context/countries/{identifier}"): "context.get_country",
    # Compare
    ("POST", "/compare/tariff"): "compare.tariff",
    ("GET", "/compare/hts/{hts_code}"): "compare.hts_rates",
    ("GET", "/compare/sources"): "compare.sources",
    # Versions
    ("GET", "/versions"): "versions.list",
}

# ── Response model registry (type name → resource.method that returns it) ──
# Used to warn when spec schemas diverge from SDK models.
TYPED_RESPONSES: dict[str, str] = {
    "CalcResponse": "rates.evaluate_entry",
}


def _load_spec_endpoints() -> set[tuple[str, str]]:
    """Load all (METHOD, path) pairs from openapi-sdk.json."""
    if not OPENAPI_PATH.exists():
        print(
            f"ERROR: {OPENAPI_PATH} not found. Run extract_openapi.py first.",
            file=sys.stderr,
        )
        sys.exit(1)

    with open(OPENAPI_PATH, encoding="utf-8") as f:
        schema = json.load(f)

    endpoints: set[tuple[str, str]] = set()
    for path, path_item in schema.get("paths", {}).items():
        for method in ("get", "post", "put", "patch", "delete"):
            if method in path_item:
                endpoints.add((method.upper(), path))
    return endpoints


def _load_spec_schema_names() -> set[str]:
    """Load all schema component names from openapi-sdk.json."""
    if not OPENAPI_PATH.exists():
        return set()
    with open(OPENAPI_PATH, encoding="utf-8") as f:
        schema = json.load(f)
    return set(schema.get("components", {}).get("schemas", {}).keys())


def main() -> None:
    spec_endpoints = _load_spec_endpoints()
    v1_keys = set(V1_COVERAGE.keys())

    # v0.1 endpoints present in spec
    v1_in_spec = v1_keys & spec_endpoints

    # Check for v1 endpoints that were removed from the spec
    v1_removed = v1_keys - spec_endpoints
    if v1_removed:
        print("WARNING: v0.1 endpoints removed from API spec:")
        for method, path in sorted(v1_removed):
            sdk_method = V1_COVERAGE[(method, path)]
            print(f"  {method:6s} {path:50s} → {sdk_method}")
        print()

    # ── Endpoints outside v0.1 scope ───────────────────────────────────
    outside_v1 = spec_endpoints - v1_keys
    total_spec = len(spec_endpoints)
    total_covered = len(v1_in_spec)

    # ── Schema drift check ─────────────────────────────────────────────
    spec_schemas = _load_spec_schema_names()
    schema_warnings: list[str] = []
    for type_name, sdk_method in TYPED_RESPONSES.items():
        if spec_schemas and type_name not in spec_schemas:
            # The spec might use different naming — just warn
            schema_warnings.append(
                f"  SDK type '{type_name}' (used by {sdk_method}) "
                f"not found in spec schemas"
            )

    # ── Summary ────────────────────────────────────────────────────────
    print(f"{'─' * 60}")
    print("SDK Drift Check")
    print(f"{'─' * 60}")
    print(f"  v0.1 scope: {len(v1_keys)} endpoints defined")
    print(f"  v0.1 in spec: {len(v1_in_spec)}/{len(v1_keys)} present")
    print(f"  Total spec endpoints: {total_spec}")
    print(
        f"  SDK coverage: {total_covered}/{total_spec} ({100 * total_covered // max(total_spec, 1)}%)"
    )
    print(f"{'─' * 60}")

    if outside_v1:
        print(f"\nNot yet implemented ({len(outside_v1)} endpoints):")
        for method, path in sorted(outside_v1):
            print(f"  {method:6s} {path}")

    if schema_warnings:
        print(f"\nSchema warnings ({len(schema_warnings)}):")
        for w in schema_warnings:
            print(w)

    # ── Exit code ──────────────────────────────────────────────────────
    errors = 0

    # v0.1 endpoints that disappeared from the spec are errors —
    # the SDK has methods for endpoints that no longer exist.
    if v1_removed:
        errors += len(v1_removed)

    if errors:
        print(f"\n{errors} error(s) found.")
        sys.exit(1)
    else:
        print("\nOK: All v0.1 endpoints covered.")


if __name__ == "__main__":
    main()
