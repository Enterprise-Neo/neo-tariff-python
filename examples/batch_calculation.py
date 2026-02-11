"""Batch duty calculation example.

Demonstrates how to evaluate multiple entries in a single request.
Returns typed CalcResponse models for each entry.

Usage:
    export NEO_TARIFF_API_KEY="ntf_your_key_here"
    python examples/batch_calculation.py
"""

import os

from neo_tariff import NeoTariff

api_key = os.environ.get("NEO_TARIFF_API_KEY", "")
if not api_key:
    raise SystemExit("Set NEO_TARIFF_API_KEY environment variable first.")

entries = [
    {
        "hts_code": "7208.10.15",
        "country_of_origin": "CN",
        "cost": 10_000,
        "qty": 1_000,
        "rec_id": "entry-1",
    },
    {
        "hts_code": "8471.30.01",
        "country_of_origin": "JP",
        "cost": 5_000,
        "qty": 100,
        "rec_id": "entry-2",
    },
    {
        "hts_code": "6110.20.20",
        "country_of_origin": "VN",
        "cost": 2_000,
        "qty": 500,
        "rec_id": "entry-3",
    },
]

with NeoTariff(api_key=api_key) as client:
    result = client.rates.evaluate_entries(data=entries)

    data = result.require_data()  # list[CalcResponse]
    print(f"Processed {len(data)} entries\n")
    for entry in data:
        rec_id = entry.inputs.get("rec_id", "?") if entry.inputs else "?"
        hts = entry.inputs.get("hts_code", "?") if entry.inputs else "?"
        total = 0.0
        if entry.summary:
            net = entry.summary.duty_totals.get("net")
            if net:
                total = net.total
        print(f"  [{rec_id}] {hts}: ${total:,.2f} duty")
