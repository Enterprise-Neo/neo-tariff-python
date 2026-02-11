"""Search resource – HTS code and document search endpoints."""

from __future__ import annotations

from typing import Any, Literal

from neo_tariff._http import _clean
from neo_tariff._types import APIResponse
from neo_tariff.resources._base import AsyncResource, SyncResource
from neo_tariff.types.search import APIRespAutocompleteHtsItem, APIRespSearchHtsItem


class SearchResource(SyncResource):
    """Synchronous search resource."""

    def hts(
        self,
        *,
        query: str | None = None,
        code: str | None = None,
        fuzzy: bool = False,
        section: str | None = None,
        chapter: str | None = None,
        limit: int = 10,
        include_notes: bool = False,
        semantic: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespSearchHtsItem]]:
        """Search HTS codes by description or code prefix.

        Calls ``GET /search/hts``.
        """
        params = _clean(
            {
                "query": query,
                "code": code,
                "fuzzy": fuzzy or None,
                "section": section,
                "chapter": chapter,
                "limit": limit,
                "include_notes": include_notes or None,
                "semantic": semantic or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            "/search/hts",
            params=params,
            response_type=list[APIRespSearchHtsItem],
        )

    def hts_docs(
        self,
        *,
        query: str,
        types: str | None = None,
        limit: int = 10,
        hint: Literal["code", "description", "notes"] | None = None,
        semantic: bool = False,
        sections_limit: int | None = None,
        chapters_limit: int | None = None,
        codes_limit: int | None = None,
        notes_limit: int | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """Search across HTS documentation (sections, chapters, codes, notes).

        Calls ``GET /search/hts-docs``.
        """
        params = _clean(
            {
                "query": query,
                "types": types,
                "limit": limit,
                "hint": hint,
                "semantic": semantic or None,
                "sections_limit": sections_limit,
                "chapters_limit": chapters_limit,
                "codes_limit": codes_limit,
                "notes_limit": notes_limit,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request("GET", "/search/hts-docs", params=params)

    def autocomplete_hts(
        self,
        *,
        prefix: str,
        limit: int = 10,
        include_4_digit: bool = True,
        include_6_digit: bool = True,
        include_8_digit: bool = True,
        include_10_digit: bool = True,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespAutocompleteHtsItem]]:
        """Autocomplete HTS codes by prefix.

        Calls ``GET /search/autocomplete/hts``.
        """
        params = _clean(
            {
                "prefix": prefix,
                "limit": limit,
                "include_4_digit": include_4_digit if not include_4_digit else None,
                "include_6_digit": include_6_digit if not include_6_digit else None,
                "include_8_digit": include_8_digit if not include_8_digit else None,
                "include_10_digit": include_10_digit if not include_10_digit else None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            "/search/autocomplete/hts",
            params=params,
            response_type=list[APIRespAutocompleteHtsItem],
        )

    def hts_by_description(
        self,
        *,
        query: str,
        limit: int = 10,
        include_4_digit: bool = True,
        include_6_digit: bool = True,
        include_8_digit: bool = True,
        include_10_digit: bool = True,
        fuzzy: bool = True,
        semantic: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespAutocompleteHtsItem]]:
        """Search HTS codes by natural language description.

        Calls ``GET /search/hts/by-description``.
        """
        params = _clean(
            {
                "query": query,
                "limit": limit,
                "include_4_digit": include_4_digit if not include_4_digit else None,
                "include_6_digit": include_6_digit if not include_6_digit else None,
                "include_8_digit": include_8_digit if not include_8_digit else None,
                "include_10_digit": include_10_digit if not include_10_digit else None,
                "fuzzy": fuzzy if not fuzzy else None,
                "semantic": semantic or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return self._http.request_typed(
            "GET",
            "/search/hts/by-description",
            params=params,
            response_type=list[APIRespAutocompleteHtsItem],
        )


class AsyncSearchResource(AsyncResource):
    """Asynchronous search resource."""

    async def hts(
        self,
        *,
        query: str | None = None,
        code: str | None = None,
        fuzzy: bool = False,
        section: str | None = None,
        chapter: str | None = None,
        limit: int = 10,
        include_notes: bool = False,
        semantic: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespSearchHtsItem]]:
        """Search HTS codes by description or code prefix.

        Calls ``GET /search/hts``.
        """
        params = _clean(
            {
                "query": query,
                "code": code,
                "fuzzy": fuzzy or None,
                "section": section,
                "chapter": chapter,
                "limit": limit,
                "include_notes": include_notes or None,
                "semantic": semantic or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            "/search/hts",
            params=params,
            response_type=list[APIRespSearchHtsItem],
        )

    async def hts_docs(
        self,
        *,
        query: str,
        types: str | None = None,
        limit: int = 10,
        hint: Literal["code", "description", "notes"] | None = None,
        semantic: bool = False,
        sections_limit: int | None = None,
        chapters_limit: int | None = None,
        codes_limit: int | None = None,
        notes_limit: int | None = None,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[Any]:
        """Search across HTS documentation (sections, chapters, codes, notes).

        Calls ``GET /search/hts-docs``.
        """
        params = _clean(
            {
                "query": query,
                "types": types,
                "limit": limit,
                "hint": hint,
                "semantic": semantic or None,
                "sections_limit": sections_limit,
                "chapters_limit": chapters_limit,
                "codes_limit": codes_limit,
                "notes_limit": notes_limit,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request("GET", "/search/hts-docs", params=params)

    async def autocomplete_hts(
        self,
        *,
        prefix: str,
        limit: int = 10,
        include_4_digit: bool = True,
        include_6_digit: bool = True,
        include_8_digit: bool = True,
        include_10_digit: bool = True,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespAutocompleteHtsItem]]:
        """Autocomplete HTS codes by prefix.

        Calls ``GET /search/autocomplete/hts``.
        """
        params = _clean(
            {
                "prefix": prefix,
                "limit": limit,
                "include_4_digit": include_4_digit if not include_4_digit else None,
                "include_6_digit": include_6_digit if not include_6_digit else None,
                "include_8_digit": include_8_digit if not include_8_digit else None,
                "include_10_digit": include_10_digit if not include_10_digit else None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            "/search/autocomplete/hts",
            params=params,
            response_type=list[APIRespAutocompleteHtsItem],
        )

    async def hts_by_description(
        self,
        *,
        query: str,
        limit: int = 10,
        include_4_digit: bool = True,
        include_6_digit: bool = True,
        include_8_digit: bool = True,
        include_10_digit: bool = True,
        fuzzy: bool = True,
        semantic: bool = False,
        hts_date: str | None = None,
        hts_year: int | None = None,
        hts_version: int | None = None,
    ) -> APIResponse[list[APIRespAutocompleteHtsItem]]:
        """Search HTS codes by natural language description.

        Calls ``GET /search/hts/by-description``.
        """
        params = _clean(
            {
                "query": query,
                "limit": limit,
                "include_4_digit": include_4_digit if not include_4_digit else None,
                "include_6_digit": include_6_digit if not include_6_digit else None,
                "include_8_digit": include_8_digit if not include_8_digit else None,
                "include_10_digit": include_10_digit if not include_10_digit else None,
                "fuzzy": fuzzy if not fuzzy else None,
                "semantic": semantic or None,
                "hts_date": hts_date,
                "hts_year": hts_year,
                "hts_version": hts_version,
            }
        )
        return await self._http.request_typed(
            "GET",
            "/search/hts/by-description",
            params=params,
            response_type=list[APIRespAutocompleteHtsItem],
        )
