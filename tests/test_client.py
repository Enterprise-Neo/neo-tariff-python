"""Unit tests for neo-tariff client and resources."""

from __future__ import annotations

import httpx
import pytest

from neo_tariff import (
    APIResponse,
    AsyncNeoTariff,
    NeoTariff,
    NeoTariffAPIError,
    NeoTariffConnectionError,
    NeoTariffHTTPError,
    NeoTariffError,
    AuthenticationError,
    NotFoundError,
    RateLimitError,
    ServerError,
    ValidationError,
)


# ── Client construction ────────────────────────────────────────────────────


class TestClientConstruction:
    def test_sync_client_has_all_resources(self, client: NeoTariff):
        assert hasattr(client, "rates")
        assert hasattr(client, "search")
        assert hasattr(client, "context")
        assert hasattr(client, "compare")
        assert hasattr(client, "versions")

    def test_async_client_has_all_resources(self, async_client: AsyncNeoTariff):
        assert hasattr(async_client, "rates")
        assert hasattr(async_client, "search")
        assert hasattr(async_client, "context")
        assert hasattr(async_client, "compare")
        assert hasattr(async_client, "versions")

    def test_sync_context_manager(self, mock_router):
        with NeoTariff(api_key="ntf_test", base_url="https://api.test.local") as c:
            assert c.rates is not None

    @pytest.mark.asyncio
    async def test_async_context_manager(self, mock_router):
        async with AsyncNeoTariff(
            api_key="ntf_test", base_url="https://api.test.local"
        ) as c:
            assert c.rates is not None


class TestEnvVarAutoDetection:
    """Test API key and base URL auto-detection from environment variables."""

    def test_sync_api_key_from_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_from_env")
        client = NeoTariff(base_url="https://api.test.local")
        assert client._http._client.headers["X-API-Key"] == "ntf_from_env"

    def test_async_api_key_from_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_from_env")
        client = AsyncNeoTariff(base_url="https://api.test.local")
        assert client._http._client.headers["X-API-Key"] == "ntf_from_env"

    def test_explicit_api_key_overrides_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_from_env")
        client = NeoTariff(api_key="ntf_explicit", base_url="https://api.test.local")
        assert client._http._client.headers["X-API-Key"] == "ntf_explicit"

    def test_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("NEO_TARIFF_API_KEY", raising=False)
        with pytest.raises(NeoTariffError, match="No API key provided"):
            NeoTariff(base_url="https://api.test.local")

    def test_async_missing_api_key_raises(self, monkeypatch):
        monkeypatch.delenv("NEO_TARIFF_API_KEY", raising=False)
        with pytest.raises(NeoTariffError, match="No API key provided"):
            AsyncNeoTariff(base_url="https://api.test.local")

    def test_base_url_from_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_BASE_URL", "https://staging.example.com")
        client = NeoTariff(api_key="ntf_test")
        assert str(client._http._client.base_url) == "https://staging.example.com"

    def test_explicit_base_url_overrides_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_BASE_URL", "https://staging.example.com")
        client = NeoTariff(api_key="ntf_test", base_url="https://custom.example.com")
        assert str(client._http._client.base_url) == "https://custom.example.com"

    def test_default_base_url_when_no_env(self, monkeypatch, mock_router):
        monkeypatch.delenv("NEO_TARIFF_BASE_URL", raising=False)
        client = NeoTariff(api_key="ntf_test")
        assert "tariff-data.enterprise-neo.com" in str(client._http._client.base_url)

    def test_zero_config_with_env_vars(self, monkeypatch, mock_router):
        """Verify the zero-config pattern: just set env vars, no constructor args."""
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_zero_config")
        monkeypatch.setenv("NEO_TARIFF_BASE_URL", "https://api.test.local")
        client = NeoTariff()
        assert client._http._client.headers["X-API-Key"] == "ntf_zero_config"
        assert str(client._http._client.base_url) == "https://api.test.local"

    def test_timeout_from_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_timeout_env")
        monkeypatch.setenv("NEO_TARIFF_BASE_URL", "https://api.test.local")
        monkeypatch.setenv("NEO_TARIFF_TIMEOUT", "12.5")
        client = NeoTariff()
        assert client._http._client.timeout.connect == 12.5

    def test_max_retries_from_env(self, monkeypatch, mock_router):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_retries_env")
        monkeypatch.setenv("NEO_TARIFF_BASE_URL", "https://api.test.local")
        monkeypatch.setenv("NEO_TARIFF_MAX_RETRIES", "7")
        client = NeoTariff()
        assert client._http._max_retries == 7

    def test_invalid_timeout_env_raises(self, monkeypatch):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_bad_timeout")
        monkeypatch.setenv("NEO_TARIFF_TIMEOUT", "not-a-number")
        with pytest.raises(NeoTariffError, match="Invalid NEO_TARIFF_TIMEOUT"):
            NeoTariff()

    def test_invalid_max_retries_env_raises(self, monkeypatch):
        monkeypatch.setenv("NEO_TARIFF_API_KEY", "ntf_bad_retries")
        monkeypatch.setenv("NEO_TARIFF_MAX_RETRIES", "not-int")
        with pytest.raises(NeoTariffError, match="Invalid NEO_TARIFF_MAX_RETRIES"):
            NeoTariff()

    def test_sync_from_env_file(self, tmp_path, monkeypatch, mock_router):
        monkeypatch.delenv("NEO_TARIFF_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "NEO_TARIFF_API_KEY=ntf_from_file",
                    "NEO_TARIFF_BASE_URL=https://api.test.local",
                    "NEO_TARIFF_TIMEOUT=11",
                    "NEO_TARIFF_MAX_RETRIES=4",
                ]
            ),
            encoding="utf-8",
        )
        client = NeoTariff.from_env_file(env_file)
        assert client._http._client.headers["X-API-Key"] == "ntf_from_file"
        assert str(client._http._client.base_url) == "https://api.test.local"
        assert client._http._client.timeout.connect == 11.0
        assert client._http._max_retries == 4

    def test_async_from_env_file(self, tmp_path, monkeypatch, mock_router):
        monkeypatch.delenv("NEO_TARIFF_API_KEY", raising=False)
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "NEO_TARIFF_API_KEY=ntf_from_file_async",
                    "NEO_TARIFF_BASE_URL=https://api.test.local",
                    "NEO_TARIFF_TIMEOUT=9",
                    "NEO_TARIFF_MAX_RETRIES=3",
                ]
            ),
            encoding="utf-8",
        )
        client = AsyncNeoTariff.from_env_file(env_file)
        assert client._http._client.headers["X-API-Key"] == "ntf_from_file_async"
        assert str(client._http._client.base_url) == "https://api.test.local"
        assert client._http._client.timeout.connect == 9.0
        assert client._http._max_retries == 3

    def test_explicit_kwargs_override_env_file(self, tmp_path, mock_router):
        env_file = tmp_path / ".env"
        env_file.write_text(
            "\n".join(
                [
                    "NEO_TARIFF_API_KEY=ntf_from_file",
                    "NEO_TARIFF_BASE_URL=https://env-file.example.com",
                    "NEO_TARIFF_TIMEOUT=8",
                    "NEO_TARIFF_MAX_RETRIES=8",
                ]
            ),
            encoding="utf-8",
        )
        client = NeoTariff.from_env_file(
            env_file,
            api_key="ntf_explicit",
            base_url="https://api.test.local",
            timeout=13.0,
            max_retries=1,
        )
        assert client._http._client.headers["X-API-Key"] == "ntf_explicit"
        assert str(client._http._client.base_url) == "https://api.test.local"
        assert client._http._client.timeout.connect == 13.0
        assert client._http._max_retries == 1

    def test_missing_env_file_raises(self):
        with pytest.raises(NeoTariffError, match="Env file not found"):
            NeoTariff.from_env_file("/tmp/does-not-exist-sdk.env")


# ── Rates resource ─────────────────────────────────────────────────────────


class TestRates:
    def test_evaluate_entry(self, client, mock_router, success_envelope):
        mock_router.post("/rates/entry").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "inputs": {"hts_code": "7208.10.15"},
                        "totals": {
                            "net": {
                                "ad_valorem": 250.0,
                                "specific": 0.0,
                                "total": 250.0,
                            }
                        },
                        "components": [],
                        "is_composite": False,
                    }
                ),
            )
        )
        result = client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        from neo_tariff.types.rates import CalcResponse

        assert isinstance(result.data, CalcResponse)
        assert result.data.totals["net"].total == 250.0

    def test_evaluate_entries(self, client, mock_router, success_envelope):
        mock_router.post("/rates/entries").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    [
                        {"totals": {}, "components": [], "is_composite": False},
                        {"totals": {}, "components": [], "is_composite": False},
                    ]
                ),
            )
        )
        result = client.rates.evaluate_entries(
            data=[
                {
                    "hts_code": "7208.10.15",
                    "country_of_origin": "CN",
                    "cost": 5000,
                    "qty": 500,
                },
                {
                    "hts_code": "7208.10.15",
                    "country_of_origin": "DE",
                    "cost": 5000,
                    "qty": 500,
                },
            ]
        )
        assert result.success is True
        assert len(result.data) == 2
        from neo_tariff.types.rates import CalcResponse

        assert isinstance(result.data[0], CalcResponse)

    def test_evaluate_multicountry(self, client, mock_router, success_envelope):
        mock_router.post("/rates/multicountry").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    [
                        {"totals": {}, "components": [], "is_composite": False},
                        {"totals": {}, "components": [], "is_composite": False},
                    ]
                ),
            )
        )
        result = client.rates.evaluate_multicountry(
            hts_code="7208.10.15",
            countries=["CN", "DE", "JP"],
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        assert isinstance(result.data, list)


# ── Search resource ────────────────────────────────────────────────────────


class TestSearch:
    def test_search_hts(self, client, mock_router, success_envelope):
        mock_router.get("/search/hts").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    [
                        {
                            "hts_code": "7208.10.15",
                            "description": "Flat-rolled products of iron",
                        }
                    ]
                ),
            )
        )
        result = client.search.hts(query="steel plates", limit=5)
        assert result.success is True
        assert isinstance(result.data, list)
        from neo_tariff.types.search import APIRespSearchHtsItem

        assert isinstance(result.data[0], APIRespSearchHtsItem)
        assert result.data[0].hts_code == "7208.10.15"

    def test_hts_docs(self, client, mock_router, success_envelope):
        mock_router.get("/search/hts-docs").mock(
            return_value=httpx.Response(200, json=success_envelope({"results": []}))
        )
        result = client.search.hts_docs(query="steel")
        assert result.success is True

    def test_autocomplete_hts(self, client, mock_router, success_envelope):
        mock_router.get("/search/autocomplete/hts").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = client.search.autocomplete_hts(prefix="7208")
        assert result.success is True

    def test_hts_by_description(self, client, mock_router, success_envelope):
        mock_router.get("/search/hts/by-description").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = client.search.hts_by_description(query="cold rolled steel sheets")
        assert result.success is True


# ── Context resource ───────────────────────────────────────────────────────


class TestContext:
    def test_list_sections(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/sections").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = client.context.list_sections()
        assert result.success is True

    def test_list_chapters_by_section(self, client, mock_router, success_envelope):
        route = mock_router.get("/context/hts/sections/1/chapters").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = client.context.list_chapters_by_section(
            "1",
            include_context=True,
            include_hts_codes=True,
        )
        assert result.success is True
        params = route.calls.last.request.url.params
        assert params["bool_context"] == "true"
        assert params["bool_hts_codes"] == "true"
        assert "include_context" not in params
        assert "include_hts_codes" not in params

    def test_get_hts_code(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/7208.10.15").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope({"hts_code": "7208.10.15"}),
            )
        )
        result = client.context.get_hts_code("7208.10.15")
        assert result.success is True

    def test_get_hts_details(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/7208.10.15/details").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "hts_code": "7208100000",
                        "description": "Flat-rolled products of iron",
                        "indent_level": 2,
                    }
                ),
            )
        )
        result = client.context.get_hts_details("7208.10.15")
        assert result.success is True
        from neo_tariff.types.context import APIRespDataHtsCodeContext

        assert isinstance(result.data, APIRespDataHtsCodeContext)
        assert result.data.hts_code == "7208100000"

    def test_get_hts_hub(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/7208.10.15/hub").mock(
            return_value=httpx.Response(200, json=success_envelope({}))
        )
        result = client.context.get_hts_hub("7208.10.15")
        assert result.success is True

    def test_get_hts_hub_batch(self, client, mock_router, success_envelope):
        mock_router.post("/context/hts/batch").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "7208.10.15": {
                            "hts_code": "7208.10.15",
                            "code_type": "leaf",
                            "basic": {},
                        }
                    }
                ),
            )
        )
        result = client.context.get_hts_hub_batch(["7208.10.15"])
        assert result.success is True
        assert "7208.10.15" in result.data

    def test_get_hts_history(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/7208.10.15/history").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    [
                        {
                            "year": 2025,
                            "version": 25,
                            "hts_entry": {"hts_code": "7208100000"},
                        }
                    ]
                ),
            )
        )
        result = client.context.get_hts_history("7208.10.15")
        assert result.success is True
        assert isinstance(result.data, list)

    def test_get_document_index(self, client, mock_router, success_envelope):
        mock_router.get("/context/hts/document-index").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {"intro": [], "general_notes": [], "appendices": []}
                ),
            )
        )
        result = client.context.get_document_index()
        assert result.success is True

    def test_get_document(self, client, mock_router, success_envelope):
        mock_router.get("/context/document/chapter-1-note").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "document_id": "chapter-1-note",
                        "document_type": "note",
                        "alias": "chapter-note",
                        "title": "Chapter 1 note",
                    }
                ),
            )
        )
        result = client.context.get_document("chapter-1-note")
        assert result.success is True

    def test_list_countries(self, client, mock_router, success_envelope):
        mock_router.get("/context/countries").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = client.context.list_countries()
        assert result.success is True

    def test_get_country(self, client, mock_router, success_envelope):
        mock_router.get("/context/countries/CN").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope({"country_name": "China", "iso_alpha2": "CN"}),
            )
        )
        result = client.context.get_country("CN")
        assert result.success is True
        from neo_tariff.types.countries import CountryRecord

        assert isinstance(result.data, CountryRecord)
        assert result.data.country_name == "China"

    def test_get_countries_batch(self, client, mock_router, success_envelope):
        mock_router.post("/context/countries/batch").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "CN": {"country_name": "China", "iso_alpha2": "CN"},
                        "DE": {"country_name": "Germany", "iso_alpha2": "DE"},
                    }
                ),
            )
        )
        result = client.context.get_countries_batch(["CN", "DE"])
        assert result.success is True
        from neo_tariff.types.countries import CountryRecord

        assert isinstance(result.data["CN"], CountryRecord)


# ── Compare resource ───────────────────────────────────────────────────────


class TestCompare:
    def test_tariff(self, client, mock_router, success_envelope):
        mock_router.post("/compare/tariff").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "CN": {"totals": {}, "components": [], "is_composite": False},
                        "DE": {"totals": {}, "components": [], "is_composite": False},
                    }
                ),
            )
        )
        result = client.compare.tariff(
            hts_code="7208.10.15",
            countries=["CN", "DE"],
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        assert isinstance(result.data, dict)
        from neo_tariff.types.rates import CalcResponse

        assert isinstance(result.data["CN"], CalcResponse)

    def test_hts_rates(self, client, mock_router, success_envelope):
        mock_router.get("/compare/hts/7208.10.15").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "hts_code": "7208.10.15",
                        "source_a": "2025-v15",
                        "source_b": "2025-v25",
                    }
                ),
            )
        )
        result = client.compare.hts_rates(
            "7208.10.15",
            year_a=2025,
            version_a=25,
        )
        assert result.success is True
        from neo_tariff.types.compare import CompareRatesResponse

        assert isinstance(result.data, CompareRatesResponse)
        assert result.data.hts_code == "7208.10.15"

    def test_sources(self, client, mock_router, success_envelope):
        mock_router.get("/compare/sources").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "source_a": "2025-v15",
                        "source_b": "2025-v25",
                        "changes": {"added": [], "removed": [], "modified": []},
                    }
                ),
            )
        )
        result = client.compare.sources(year_a=2025, version_a=25)
        assert result.success is True
        from neo_tariff.types.compare import CompareSourcesResponse

        assert isinstance(result.data, CompareSourcesResponse)
        assert result.data.source_a == "2025-v15"


# ── Versions resource ──────────────────────────────────────────────────────


class TestVersions:
    def test_list(self, client, mock_router, success_envelope):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope([{"year": 2025, "version": 25}]),
            )
        )
        result = client.versions.list()
        assert result.success is True
        assert isinstance(result.data, list)


# ── Error handling ─────────────────────────────────────────────────────────


class TestErrorHandling:
    def test_authentication_error(self, client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                401,
                json={"detail": "Invalid API key"},
            )
        )
        with pytest.raises(AuthenticationError) as exc_info:
            client.versions.list()
        assert exc_info.value.status_code == 401
        assert "Invalid API key" in str(exc_info.value)

    def test_not_found_error(self, client, mock_router):
        mock_router.get("/context/hts/INVALID").mock(
            return_value=httpx.Response(404, json={"detail": "Not found"})
        )
        with pytest.raises(NotFoundError) as exc_info:
            client.context.get_hts_code("INVALID")
        assert exc_info.value.status_code == 404

    def test_validation_error(self, client, mock_router):
        mock_router.post("/rates/entry").mock(
            return_value=httpx.Response(
                422,
                json={
                    "detail": [
                        {
                            "loc": ["body", "hts_code"],
                            "msg": "field required",
                            "type": "value_error",
                        }
                    ]
                },
            )
        )
        with pytest.raises(ValidationError) as exc_info:
            client.rates.evaluate_entry(
                hts_code="",
                country_of_origin="CN",
                cost=0,
                qty=0,
            )
        assert exc_info.value.status_code == 422

    def test_rate_limit_error(self, client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(429, json={"detail": "Too many requests"})
        )
        with pytest.raises(RateLimitError):
            client.versions.list()

    def test_server_error(self, client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(500, json={"detail": "Internal error"})
        )
        with pytest.raises(ServerError) as exc_info:
            client.versions.list()
        assert exc_info.value.status_code == 500

    def test_api_error_success_false(self, client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                200,
                json={
                    "success": False,
                    "errors": [{"code": "ERR_001", "message": "Something went wrong"}],
                    "data": None,
                    "meta": None,
                },
            )
        )
        with pytest.raises(NeoTariffAPIError) as exc_info:
            client.versions.list()
        assert "Something went wrong" in str(exc_info.value)

    def test_non_json_error_response(self, client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                502,
                text="<html>Bad Gateway</html>",
                headers={"content-type": "text/html"},
            )
        )
        with pytest.raises(ServerError) as exc_info:
            client.versions.list()
        assert exc_info.value.raw_body is not None

    def test_connection_error(self, mock_router):
        mock_router.get("/versions").mock(side_effect=httpx.ConnectError("refused"))
        client = NeoTariff(api_key="ntf_test", base_url="https://api.test.local")
        with pytest.raises(NeoTariffConnectionError):
            client.versions.list()


# ── APIResponse helpers ────────────────────────────────────────────────────


class TestAPIResponse:
    def test_require_data_returns_data(self, client, mock_router, success_envelope):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope([{"year": 2025}]),
            )
        )
        result = client.versions.list()
        data = result.require_data()
        assert isinstance(data, list)

    def test_require_data_raises_on_none(self):
        resp = APIResponse(success=True, data=None)
        with pytest.raises(NeoTariffError, match="no data"):
            resp.require_data()

    def test_exception_hierarchy(self):
        assert issubclass(NeoTariffHTTPError, NeoTariffError)
        assert issubclass(AuthenticationError, NeoTariffHTTPError)
        assert issubclass(NotFoundError, NeoTariffHTTPError)
        assert issubclass(ValidationError, NeoTariffHTTPError)
        assert issubclass(RateLimitError, NeoTariffHTTPError)
        assert issubclass(ServerError, NeoTariffHTTPError)
        assert issubclass(NeoTariffAPIError, NeoTariffError)
        assert issubclass(NeoTariffConnectionError, NeoTariffError)


# ── Async resource tests ──────────────────────────────────────────────────


class TestAsyncResources:
    @pytest.mark.asyncio
    async def test_async_evaluate_entry(
        self, async_client, mock_router, success_envelope
    ):
        mock_router.post("/rates/entry").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope(
                    {
                        "inputs": {"hts_code": "7208.10.15"},
                        "totals": {
                            "net": {
                                "ad_valorem": 250.0,
                                "specific": 0.0,
                                "total": 250.0,
                            }
                        },
                        "components": [],
                        "is_composite": False,
                    }
                ),
            )
        )
        result = await async_client.rates.evaluate_entry(
            hts_code="7208.10.15",
            country_of_origin="CN",
            cost=10000,
            qty=1000,
        )
        assert result.success is True
        from neo_tariff.types.rates import CalcResponse

        assert isinstance(result.data, CalcResponse)
        assert result.data.totals["net"].total == 250.0

    @pytest.mark.asyncio
    async def test_async_search_hts(self, async_client, mock_router, success_envelope):
        mock_router.get("/search/hts").mock(
            return_value=httpx.Response(200, json=success_envelope([]))
        )
        result = await async_client.search.hts(query="steel")
        assert result.success is True

    @pytest.mark.asyncio
    async def test_async_versions_list(
        self, async_client, mock_router, success_envelope
    ):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(
                200,
                json=success_envelope([{"year": 2025}]),
            )
        )
        result = await async_client.versions.list()
        assert result.success is True

    @pytest.mark.asyncio
    async def test_async_error_handling(self, async_client, mock_router):
        mock_router.get("/versions").mock(
            return_value=httpx.Response(401, json={"detail": "Unauthorized"})
        )
        with pytest.raises(AuthenticationError):
            await async_client.versions.list()
