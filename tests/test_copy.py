import copy
import gc
import random
import tracemalloc
import uuid

import pytest

from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy

_MD_Classes = type[MultiDict[int]] | type[CIMultiDict[int]]
_MDP_Classes = type[MultiDictProxy[int]] | type[CIMultiDictProxy[int]]


@pytest.fixture(scope="module")
def large_multidict() -> MultiDict[int]:
    d: MultiDict[int] = MultiDict()
    for _ in range(100000):
        d.add(str(uuid.uuid4()), random.randint(0, 100000))
    return d


def test_copy_no_memory_leak(large_multidict: MultiDict[int]) -> None:
    # Warm up to allow any initial allocations
    for _ in range(10):
        large_multidict.copy()

    gc.collect()
    tracemalloc.start()

    snap1 = tracemalloc.take_snapshot()

    # Execute 1000 copy operations
    for _ in range(1000):
        large_multidict.copy()

    gc.collect()
    snap2 = tracemalloc.take_snapshot()
    tracemalloc.stop()

    size1 = sum(stat.size for stat in snap1.statistics('lineno'))
    size2 = sum(stat.size for stat in snap2.statistics('lineno'))

    # Assert memory growth is below 5%
    growth = (size2 - size1) / size1 if size1 > 0 else 0
    assert growth < 0.05, f"Memory grew by {growth:.2%}"


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
