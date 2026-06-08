from multidict._multidict_py import MultiDict as PyMultiDict

md = PyMultiDict([('a', 1), ('b', 2)])
md.update({'a': 10, 'b': 20}, a=100, c=30)
print('Items:', list(md.items()))
print('Len:', len(md))
assert list(md.items()) == [('a', 100), ('b', 20), ('c', 30)], f'Expected [(a,100),(b,20),(c,30)], got {list(md.items())}'
assert len(md) == 3, f'Expected len=3, got len={len(md)}'
print('PASS!')

md2 = PyMultiDict([('a', 1)])
md2.merge({'a': 10}, a=100, b=20)
print('Merge items:', list(md2.items()))
print('Merge len:', len(md2))
print('PASS!')
