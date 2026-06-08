import copy
import gc
import random
import tracemalloc

import pytest

from multidict import CIMultiDict, CIMultiDictProxy, MultiDict, MultiDictProxy

_MD_Classes = type[MultiDict[int]] | type[CIMultiDict[int]]
_MDP_Classes = type[MultiDictProxy[int]] | type[CIMultiDictProxy[int]]

_NUM_KEYS = 100_000
_NUM_COPIES = 1000
_MAX_MEMORY_GROWTH_RATIO = 0.05


@pytest.fixture(scope="session")
def large_multidict_data() -> list[tuple[str, str]]:
    rng = random.Random(42)
    return [(f"key_{i}_{rng.randint(0, 999999)}", f"val_{rng.randint(0, 999999)}") for i in range(_NUM_KEYS)]


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


def test_copy_no_memory_leak(
    any_multidict_class: _MD_Classes,
    large_multidict_data: list[tuple[str, str]],
) -> None:
    d = any_multidict_class(large_multidict_data)

    gc.collect()
    tracemalloc.start()

    snapshot_before = tracemalloc.take_snapshot()

    for _ in range(_NUM_COPIES):
        _ = d.copy()

    gc.collect()
    snapshot_after = tracemalloc.take_snapshot()

    tracemalloc.stop()

    stats_before = snapshot_before.statistics("lineno")
    stats_after = snapshot_after.statistics("lineno")

    mem_before = sum(s.size for s in stats_before)
    mem_after = sum(s.size for s in stats_after)

    growth = (mem_after - mem_before) / mem_before if mem_before > 0 else 0
    assert growth < _MAX_MEMORY_GROWTH_RATIO, (
        f"Memory grew by {growth:.2%} after {_NUM_COPIES} copy() calls "
        f"(threshold: {_MAX_MEMORY_GROWTH_RATIO:.0%}). "
        f"Before: {mem_before / 1024:.1f} KiB, After: {mem_after / 1024:.1f} KiB"
    )
