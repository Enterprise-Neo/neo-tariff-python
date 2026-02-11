"""Shared test fixtures for neo-tariff tests."""

from __future__ import annotations

import pytest
import respx

from neo_tariff import AsyncNeoTariff, NeoTariff

TEST_BASE_URL = "https://api.test.local"
TEST_API_KEY = "ntf_test_key_12345"


def _success_envelope(data=None, *, operation: str = "test"):
    """Build a standard API success envelope."""
    return {
        "success": True,
        "meta": {
            "timestamp_unixts": 1700000000.0,
            "operation": operation,
            "params": {},
            "hts_year": 2025,
            "hts_version": 25,
        },
        "data": data,
        "errors": None,
    }


@pytest.fixture()
def base_url() -> str:
    return TEST_BASE_URL


@pytest.fixture()
def api_key() -> str:
    return TEST_API_KEY


@pytest.fixture()
def mock_router():
    """Provide a respx mock router for httpx calls."""
    with respx.mock(base_url=TEST_BASE_URL) as router:
        yield router


@pytest.fixture()
def client(mock_router) -> NeoTariff:
    """Create a sync NeoTariff pointing at the mock router."""
    return NeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)


@pytest.fixture()
def async_client(mock_router) -> AsyncNeoTariff:
    """Create an async NeoTariff pointing at the mock router."""
    return AsyncNeoTariff(api_key=TEST_API_KEY, base_url=TEST_BASE_URL)


@pytest.fixture()
def success_envelope():
    """Return the helper function for building success envelopes."""
    return _success_envelope
