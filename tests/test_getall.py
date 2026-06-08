import pytest
from multidict import MultiDict, CIMultiDict


def test_getall_basic():
    md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
    assert md.getall('a') == [1, 3]
    assert md.getall('b') == [2]
    assert md.getall('c', []) == []
    assert md.getall('c', default=[42]) == [42]
    
    with pytest.raises(KeyError):
        md.getall('c')


def test_getall_cimultidict():
    md = CIMultiDict([('A', 1), ('b', 2), ('a', 3)])
    assert md.getall('a') == [1, 3]
    assert md.getall('A') == [1, 3]
    assert md.getall('b') == [2]
    assert md.getall('c', []) == []
    assert md.getall('c', default=[42]) == [42]
    
    with pytest.raises(KeyError):
        md.getall('c')


def test_getall_proxy():
    md = MultiDict([('a', 1), ('b', 2), ('a', 3)])
    proxy = md.copy()
    assert proxy.getall('a') == [1, 3]
    assert proxy.getall('b') == [2]
    
    ci_md = CIMultiDict([('A', 1), ('b', 2), ('a', 3)])
    ci_proxy = ci_md.copy()
    assert ci_proxy.getall('a') == [1, 3]
    assert ci_proxy.getall('A') == [1, 3]
