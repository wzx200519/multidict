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


@pytest.fixture(scope="session")
def large_random_multidict_items() -> list[tuple[str, str]]:
    randomizer = random.Random(0)
    return [
        (
            f"key-{index}-{randomizer.getrandbits(64):016x}",
            f"value-{randomizer.getrandbits(64):016x}",
        )
        for index in range(100_000)
    ]


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


@pytest.mark.skipif(IS_PYPY, reason="tracemalloc assertions are not stable on PyPy")
def test_copy_no_memory_leak(
    case_sensitive_multidict_class: type[MultiDict[str]],
    large_random_multidict_items: list[tuple[str, str]],
) -> None:
    tracemalloc.start()

    try:
        original = case_sensitive_multidict_class(large_random_multidict_items)
        copied = original.copy()
        del copied
        gc.collect()
        baseline_memory, _ = tracemalloc.get_traced_memory()

        for _ in range(1000):
            copied = original.copy()
            del copied

        gc.collect()
        current_memory, _ = tracemalloc.get_traced_memory()
    finally:
        tracemalloc.stop()

    assert current_memory <= baseline_memory * 1.05, (
        f"expected memory growth below 5%, got baseline={baseline_memory}, "
        f"current={current_memory}"
    )
