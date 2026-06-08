import copy
import gc
import platform
import random
import tracemalloc

import pytest

from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy

_MD_Classes = type[MultiDict[int]] | type[CIMultiDict[int]]
_MDP_Classes = type[MultiDictProxy[int]] | type[CIMultiDictProxy[int]]

IS_PYPY = platform.python_implementation() == "PyPy"

_LARGE_SIZE = 100_000
_COPY_COUNT = 1000
_MEMORY_GROWTH_THRESHOLD = 0.05
_SEED = 42


def test_copy(any_multidict_class: _MD_Classes) -> None:
    d = any_multidict_class()
    d["foo"] = 6
    d2 = d.copy()
    d2["foo"] = 7
    assert d["foo"] == 6
    assert d2["foo"] == 7


def test_copy_proxy(
    any_multidict_class: _MD_Classes, any_multidict_proxy_class: _MDP_Classes
) -> None:
    d = any_multidict_class()
    d["foo"] = 6
    p = any_multidict_proxy_class(d)
    d2 = p.copy()
    d2["foo"] = 7
    assert d["foo"] == 6
    assert p["foo"] == 6
    assert d2["foo"] == 7


def test_copy_std_copy(any_multidict_class: _MD_Classes) -> None:
    d = any_multidict_class()
    d["foo"] = 6
    d2 = copy.copy(d)
    d2["foo"] = 7
    assert d["foo"] == 6
    assert d2["foo"] == 7


def test_ci_multidict_clone(any_multidict_class: _MD_Classes) -> None:
    d = any_multidict_class(foo=6)
    d2 = any_multidict_class(d)
    d2["foo"] = 7
    assert d["foo"] == 6
    assert d2["foo"] == 7


@pytest.fixture(scope="session")
def large_multidict(any_multidict_class: _MD_Classes) -> MultiDict[int]:
    random.seed(_SEED)
    d = any_multidict_class()
    for i in range(_LARGE_SIZE):
        key = f"key_{random.randint(0, 999_999)}_{i}"
        d.add(key, random.randint(0, 999_999))
    return d


@pytest.mark.skipif(IS_PYPY, reason="tracemalloc is not reliable on PyPy")
def test_copy_no_memory_leak(large_multidict: MultiDict[int]) -> None:
    tracemalloc.start()
    gc.collect()
    baseline_current, _ = tracemalloc.get_traced_memory()

    if baseline_current == 0:
        tracemalloc.stop()
        pytest.skip("tracemalloc returned 0 baseline memory")

    copies = [large_multidict.copy() for _ in range(_COPY_COUNT)]
    del copies
    gc.collect()

    after_current, _ = tracemalloc.get_traced_memory()
    tracemalloc.stop()

    if after_current <= baseline_current:
        return

    growth = (after_current - baseline_current) / baseline_current
    assert growth < _MEMORY_GROWTH_THRESHOLD, (
        f"Memory grew by {growth:.2%}, "
        f"exceeding {_MEMORY_GROWTH_THRESHOLD:.0%} threshold"
    )
