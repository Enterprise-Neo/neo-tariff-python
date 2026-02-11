"""Tests for with_raw_response transport-swapping pattern."""

from __future__ import annotations

import httpx
import respx

from neo_tariff import AsyncNeoTariff, NeoTariff
from neo_tariff._http import RawResponse

TEST_BASE_URL = "https://api.test.local"
TEST_API_KEY = "ntf_test_key_12345"


class TestRawResponse:
    """Tests for client.with_raw_response access pattern."""

    def test_raw_versions_list_success(self):
        """with_raw_response.versions.list() should return RawResponse."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            router.get("/versions").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "success": True,
                        "data": [{"year": 2025}],
                        "meta": None,
                        "errors": None,
                    },
                )
            )
            client = NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            raw = client.with_raw_response.versions.list()
            assert isinstance(raw, RawResponse)
            assert raw.http_response.status_code == 200
            assert raw.parsed is not None
            assert raw.parsed.success is True

    def test_raw_does_not_raise_on_error(self):
        """with_raw_response should not raise on HTTP errors."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            router.get("/versions").mock(
                return_value=httpx.Response(500, json={"detail": "Internal error"})
            )
            client = NeoTariff(
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
                max_retries=0,
            )
            raw = client.with_raw_response.versions.list()
            assert isinstance(raw, RawResponse)
            assert raw.http_response.status_code == 500

    def test_raw_rates_evaluate_entry(self):
        """with_raw_response.rates.evaluate_entry() should work."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            router.post("/rates/entry").mock(
                return_value=httpx.Response(
                    200,
                    json={
                        "success": True,
                        "data": {"inputs": None, "totals": {}},
                        "meta": None,
                        "errors": None,
                    },
                )
            )
            client = NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            raw = client.with_raw_response.rates.evaluate_entry(
                hts_code="7208.10.15",
                country_of_origin="CN",
                cost=10000,
                qty=1000,
            )
            assert isinstance(raw, RawResponse)
            assert raw.http_response.status_code == 200

    def test_with_raw_response_returns_client_instance(self):
        """with_raw_response should return a NeoTariff/AsyncNeoTariff instance."""
        with respx.mock(base_url=TEST_BASE_URL):
            sync = NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            raw_sync = sync.with_raw_response
            assert isinstance(raw_sync, NeoTariff)
            assert hasattr(raw_sync, "rates")
            assert hasattr(raw_sync, "search")
            assert hasattr(raw_sync, "context")
            assert hasattr(raw_sync, "compare")
            assert hasattr(raw_sync, "versions")

            async_ = AsyncNeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)
            raw_async = async_.with_raw_response
            assert isinstance(raw_async, AsyncNeoTariff)
            assert hasattr(raw_async, "rates")
            assert hasattr(raw_async, "search")
            assert hasattr(raw_async, "context")
            assert hasattr(raw_async, "compare")
            assert hasattr(raw_async, "versions")
