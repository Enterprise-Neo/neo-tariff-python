"""Basic duty calculation example.

Demonstrates how to calculate import duties for a single HTS code.

Usage:
    export NEO_TARIFF_API_KEY="ntf_your_key_here"
    python examples/basic_duty_calc.py
"""

import os

from neo_tariff import NeoTariff

api_key = os.environ.get("NEO_TARIFF_API_KEY", "")
if not api_key:
    raise SystemExit("Set NEO_TARIFF_API_KEY environment variable first.")

with NeoTariff(api_key=api_key) as client:
    result = client.rates.evaluate_entry(
        hts_code="7208.10.15",
        country_of_origin="CN",
        cost=10_000,
        qty=1_000,
    )

    data = result.data
    print(f"HTS Code: {data.inputs['hts_code']}")
    print(f"Country:  {data.inputs['country_of_origin']}")
    print(f"Cost:     ${data.inputs['cost']:,.2f}")

    if data.summary:
        net = data.summary.duty_totals.get("net") if data.summary.duty_totals else None
        if net:
            print(f"\nTotal duty: ${net.total:,.2f}")
            print(f"  Ad valorem: ${net.percent_based:,.2f}")
            print(f"  Specific:   ${net.unit_based:,.2f}")

    if data.reciprocal and data.reciprocal.totals:
        recip = data.reciprocal.totals
        print(f"\nReciprocal additional duty: ${recip.additional_duty_amount:,.2f}")
        print(f"Reciprocal additional rate: {recip.additional_rate:.1%}")
