"""Tests for typed response models and TypeAdapter-based parsing."""

from __future__ import annotations

import httpx
import respx

from neo_tariff import NeoTariff
from neo_tariff.types.rates import CalcResponse, V3DutyTotals

TEST_BASE_URL = "https://api.test.local"
TEST_API_KEY = "ntf_test_key_12345"


def _calc_envelope(data: dict) -> dict:
    """Wrap calc data in a standard API envelope."""
    return {
        "success": True,
        "data": data,
        "meta": {
            "timestamp_unixts": 1700000000.0,
            "operation": "rates.evaluate_entry",
            "params": {},
            "hts_year": 2025,
            "hts_version": 25,
        },
        "errors": None,
    }


class TestTypedResponses:
    """Tests verifying that responses are deserialized into typed models."""

    def test_evaluate_entry_returns_calc_response(self):
        """evaluate_entry should return APIResponse[CalcResponse]."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            router.post("/rates/entry").mock(
                return_value=httpx.Response(
                    200,
                    json=_calc_envelope(
                        {
                            "inputs": {
                                "hts_code": "7208.10.15",
                                "country_of_origin": "CN",
                                "cost": 10000,
                                "qty": 1000,
                            },
                            "inputs_context": None,
                            "totals": {
                                "base": {
                                    "ad_valorem": 250.0,
                                    "specific": 0.0,
                                    "total": 250.0,
                                },
                                "net": {
                                    "ad_valorem": 2750.0,
                                    "specific": 0.0,
                                    "total": 2750.0,
                                },
                            },
                            "components": [],
                            "is_composite": False,
                            "reciprocal": {
                                "error": None,
                                "context": None,
                                "totals": {
                                    "additional_rate": 0.25,
                                    "additional_duty_amount": 2500.0,
                                },
                                "rules": [],
                                "conditional_exemptions": [],
                            },
                            "summary": {
                                "currency_code": "USD",
                                "cargo_value": {"amount": 10000, "currency": "USD"},
                                "duty_totals": {
                                    "base": {
                                        "percent_based": 250.0,
                                        "unit_based": 0.0,
                                        "total": 250.0,
                                    },
                                    "net": {
                                        "percent_based": 2750.0,
                                        "unit_based": 0.0,
                                        "total": 2750.0,
                                    },
                                },
                                "effective_rates": {},
                                "valuation_basis": {
                                    "label": "declared_value",
                                    "amount": 10000,
                                    "currency": "USD",
                                },
                                "flags": {"has_reciprocal": True},
                            },
                        }
                    ),
                )
            )
            client = NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            result = client.rates.evaluate_entry(
                hts_code="7208.10.15",
                country_of_origin="CN",
                cost=10000,
                qty=1000,
            )
            assert result.success is True

            # data should be a CalcResponse model
            data = result.data
            assert isinstance(data, CalcResponse)

            # Verify nested typed fields
            assert data.totals["base"].total == 250.0
            assert data.totals["net"].total == 2750.0
            assert data.reciprocal is not None
            assert data.reciprocal.totals.additional_rate == 0.25
            assert data.summary is not None
            assert data.summary.currency_code == "USD"
            assert data.summary.flags.has_reciprocal is True

    def test_calc_response_extra_fields_preserved(self):
        """Extra/unknown fields from the API should be preserved (not dropped)."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            router.post("/rates/entry").mock(
                return_value=httpx.Response(
                    200,
                    json=_calc_envelope(
                        {
                            "inputs": None,
                            "totals": {},
                            "components": [],
                            "is_composite": False,
                            "some_future_field": "hello",
                        }
                    ),
                )
            )
            client = NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            result = client.rates.evaluate_entry(
                hts_code="7208.10.15",
                country_of_origin="CN",
                cost=10000,
                qty=1000,
            )
            data = result.data
            assert isinstance(data, CalcResponse)
            # extra="allow" should preserve unknown fields
            assert data.some_future_field == "hello"  # type: ignore[attr-defined]

    def test_v3_duty_totals_model(self):
        """V3DutyTotals should parse correctly with defaults."""
        totals = V3DutyTotals(percent_based=100.0, unit_based=50.0, total=150.0)
        assert totals.total == 150.0

        # Defaults should work
        empty = V3DutyTotals()
        assert empty.total == 0.0

    def test_calc_response_minimal(self):
        """CalcResponse should work with minimal fields."""
        resp = CalcResponse()
        assert resp.inputs is None
        assert resp.totals == {}
        assert resp.components == []
        assert resp.is_composite is False
