"""Tests for retry logic and exponential backoff."""

from __future__ import annotations

from unittest.mock import patch

import httpx
import pytest
import respx

from neo_tariff import NeoTariff
from neo_tariff.exceptions import ServerError, NeoTariffConnectionError


TEST_BASE_URL = "https://api.test.local"
TEST_API_KEY = "ntf_test_key_12345"


class TestRetryLogic:
    """Tests for the transport-level retry mechanism."""

    def test_retries_on_500_then_succeeds(self):
        """Should retry on 500 and succeed on subsequent attempt."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.side_effect = [
                httpx.Response(500, json={"detail": "Internal error"}),
                httpx.Response(
                    200,
                    json={
                        "success": True,
                        "data": [{"year": 2025}],
                        "meta": None,
                        "errors": None,
                    },
                ),
            ]
            with patch("neo_tariff._http.time.sleep"):
                client = NeoTariff(
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                    max_retries=2,
                )
                result = client.versions.list()
                assert result.success is True
                assert route.call_count == 2

    def test_retries_on_429_then_succeeds(self):
        """Should retry on 429 rate-limit and succeed."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.side_effect = [
                httpx.Response(429, json={"detail": "Too many requests"}),
                httpx.Response(
                    200,
                    json={
                        "success": True,
                        "data": [],
                        "meta": None,
                        "errors": None,
                    },
                ),
            ]
            with patch("neo_tariff._http.time.sleep"):
                client = NeoTariff(
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                    max_retries=2,
                )
                result = client.versions.list()
                assert result.success is True
                assert route.call_count == 2

    def test_retries_exhausted_raises_server_error(self):
        """After exhausting retries, should raise the final HTTP error."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.mock(return_value=httpx.Response(502, json={"detail": "Bad gateway"}))
            with patch("neo_tariff._http.time.sleep"):
                client = NeoTariff(
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                    max_retries=2,
                )
                with pytest.raises(ServerError) as exc_info:
                    client.versions.list()
                assert exc_info.value.status_code == 502
                assert route.call_count == 3  # 1 initial + 2 retries

    def test_retries_on_connection_error(self):
        """Should retry on network errors and raise NeoTariffConnectionError."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.mock(side_effect=httpx.ConnectError("refused"))
            with patch("neo_tariff._http.time.sleep"):
                client = NeoTariff(
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                    max_retries=1,
                )
                with pytest.raises(NeoTariffConnectionError):
                    client.versions.list()
                assert route.call_count == 2  # 1 initial + 1 retry

    def test_no_retry_on_4xx(self):
        """Should NOT retry on non-retryable 4xx errors (e.g. 401, 404)."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.mock(
                return_value=httpx.Response(401, json={"detail": "Unauthorized"})
            )
            client = NeoTariff(
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
                max_retries=2,
            )
            with pytest.raises(Exception):
                client.versions.list()
            assert route.call_count == 1  # no retries

    def test_max_retries_zero_means_no_retry(self):
        """max_retries=0 should disable retries entirely."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.mock(return_value=httpx.Response(500, json={"detail": "error"}))
            client = NeoTariff(
                api_key=TEST_API_KEY,
                base_url=TEST_BASE_URL,
                max_retries=0,
            )
            with pytest.raises(ServerError):
                client.versions.list()
            assert route.call_count == 1

    def test_connection_error_then_success(self):
        """Should recover after a transient network error."""
        with respx.mock(base_url=TEST_BASE_URL) as router:
            route = router.get("/versions")
            route.side_effect = [
                httpx.ConnectError("refused"),
                httpx.Response(
                    200,
                    json={
                        "success": True,
                        "data": [],
                        "meta": None,
                        "errors": None,
                    },
                ),
            ]
            with patch("neo_tariff._http.time.sleep"):
                client = NeoTariff(
                    api_key=TEST_API_KEY,
                    base_url=TEST_BASE_URL,
                    max_retries=2,
                )
                result = client.versions.list()
                assert result.success is True

    def test_retry_after_header_respected(self):
        """Should respect Retry-After header in backoff computation."""
        from neo_tariff._http import _compute_backoff

        # Create a mock response with Retry-After
        resp = httpx.Response(429, headers={"Retry-After": "5"})
        backoff = _compute_backoff(0, resp)
        # Backoff should be at least 5 (from header), not just 0.5 (base)
        assert backoff >= 5.0
