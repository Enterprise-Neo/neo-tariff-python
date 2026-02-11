"""Sync/async parity tests.

Ensures every sync resource method has an async counterpart with the same
signature (minus async/await).
"""

from __future__ import annotations

import inspect

import pytest

from neo_tariff.resources import (
    AsyncCompareResource,
    AsyncContextResource,
    AsyncRatesResource,
    AsyncSearchResource,
    AsyncVersionsResource,
    CompareResource,
    ContextResource,
    RatesResource,
    SearchResource,
    VersionsResource,
)

_SYNC_ASYNC_PAIRS = [
    (RatesResource, AsyncRatesResource),
    (SearchResource, AsyncSearchResource),
    (ContextResource, AsyncContextResource),
    (CompareResource, AsyncCompareResource),
    (VersionsResource, AsyncVersionsResource),
]


def _public_methods(cls: type) -> dict[str, inspect.Signature]:
    """Return {name: signature} for all public methods of *cls*."""
    result = {}
    for name, method in inspect.getmembers(cls, predicate=inspect.isfunction):
        if name.startswith("_"):
            continue
        result[name] = inspect.signature(method)
    return result


class TestSyncAsyncParity:
    """Verify all sync resources have matching async counterparts."""

    @pytest.mark.parametrize(
        "sync_cls, async_cls",
        _SYNC_ASYNC_PAIRS,
        ids=[f"{s.__name__}" for s, _ in _SYNC_ASYNC_PAIRS],
    )
    def test_method_names_match(self, sync_cls: type, async_cls: type) -> None:
        """Every public method in the sync resource exists in async."""
        sync_methods = _public_methods(sync_cls)
        async_methods = _public_methods(async_cls)
        missing = set(sync_methods) - set(async_methods)
        assert not missing, f"{async_cls.__name__} missing methods: {missing}"

    @pytest.mark.parametrize(
        "sync_cls, async_cls",
        _SYNC_ASYNC_PAIRS,
        ids=[f"{s.__name__}" for s, _ in _SYNC_ASYNC_PAIRS],
    )
    def test_method_params_match(self, sync_cls: type, async_cls: type) -> None:
        """Parameter names should match between sync and async methods."""
        sync_methods = _public_methods(sync_cls)
        async_methods = _public_methods(async_cls)

        for name in sync_methods:
            if name not in async_methods:
                continue  # tested separately
            sync_params = list(sync_methods[name].parameters.keys())
            async_params = list(async_methods[name].parameters.keys())
            assert sync_params == async_params, (
                f"{name}() params differ: sync={sync_params} async={async_params}"
            )

    @pytest.mark.parametrize(
        "sync_cls, async_cls",
        _SYNC_ASYNC_PAIRS,
        ids=[f"{s.__name__}" for s, _ in _SYNC_ASYNC_PAIRS],
    )
    def test_async_methods_are_coroutines(
        self, sync_cls: type, async_cls: type
    ) -> None:
        """Every public method on the async resource should be a coroutine."""
        for name in _public_methods(sync_cls):
            async_method = getattr(async_cls, name, None)
            if async_method is None:
                continue
            assert inspect.iscoroutinefunction(async_method), (
                f"{async_cls.__name__}.{name}() is not a coroutine"
            )
