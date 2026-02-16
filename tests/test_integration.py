"""Integration tests — run against a real API endpoint.

Skipped unless NEO_TARIFF_TEST_API_KEY is set in the environment.

Usage::

    # Against production
    NEO_TARIFF_TEST_API_KEY=ntf_xxx python -m pytest tests/test_integration.py -m integration -v

    # Against local dev server
    NEO_TARIFF_TEST_API_KEY=ntf_xxx NEO_TARIFF_TEST_BASE_URL=http://localhost:8050 \
        python -m pytest tests/test_integration.py -m integration -v
"""

from __future__ import annotations

import os

import pytest

from neo_tariff import AsyncNeoTariff, NeoTariff

pytestmark = pytest.mark.integration

_SKIP_REASON = "Set NEO_TARIFF_TEST_API_KEY to run integration tests"


@pytest.fixture()
def live_client():
    api_key = os.environ.get("NEO_TARIFF_TEST_API_KEY")
    if not api_key:
        pytest.skip(_SKIP_REASON)
    base_url = os.environ.get(
        "NEO_TARIFF_TEST_BASE_URL", "https://tariff-data.enterprise-neo.com"
    )
    return NeoTariff(api_key=api_key, base_url=base_url)


@pytest.fixture()
def live_async_client():
    api_key = os.environ.get("NEO_TARIFF_TEST_API_KEY")
    if not api_key:
        pytest.skip(_SKIP_REASON)
    base_url = os.environ.get(
        "NEO_TARIFF_TEST_BASE_URL", "https://tariff-data.enterprise-neo.com"
    )
    return AsyncNeoTariff(api_key=api_key, base_url=base_url)


class TestIntegrationSmoke:
    """Smoke tests verifying basic SDK→API connectivity and response parsing."""

    def test_versions_list(self, live_client):
        result = live_client.versions.list()
        assert result.success is True
        versions = result.require_data()
        assert len(versions) > 0

    def test_search_hts(self, live_client):
        result = live_client.search.hts(query="steel", limit=3)
        assert result.success is True
        assert result.data is not None

    def test_evaluate_entry(self, live_client):
        result = live_client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        assert result.data is not None

    def test_context_country(self, live_client):
        result = live_client.context.get_country("CN")
        assert result.success is True
        assert result.data.country_name == "China"

    def test_list_sections(self, live_client):
        result = live_client.context.list_sections()
        assert result.success is True
        assert result.data is not None

    def test_autocomplete(self, live_client):
        result = live_client.search.autocomplete_hts(prefix="7208", limit=5)
        assert result.success is True


class TestIntegrationAsync:
    """Async variants of smoke tests."""

    @pytest.mark.asyncio
    async def test_async_versions_list(self, live_async_client):
        result = await live_async_client.versions.list()
        assert result.success is True
        assert len(result.require_data()) > 0

    @pytest.mark.asyncio
    async def test_async_evaluate_entry(self, live_async_client):
        result = await live_async_client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        assert result.data is not None
