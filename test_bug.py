from multidict._multidict_py import MultiDict

d = MultiDict()
d.update({'a': 1}, a=2)
print('Test 1 - len:', len(d), 'items:', list(d.items()))

d2 = MultiDict([('a', 0)])
d2.update({'a': 1}, a=2)
print('Test 2 - len:', len(d2), 'items:', list(d2.items()))

d3 = MultiDict([('b', 10), ('c', 20)])
d3.update({'a': 1}, a=2)
print('Test 3 - len:', len(d3), 'items:', list(d3.items()))

d4 = MultiDict()
d5 = MultiDict([('a', 1), ('a', 2)])
d4.update(d5, a=3)
print('Test 4 - len:', len(d4), 'items:', list(d4.items()))

d6 = MultiDict()
d6.update([('a', 1)], a=2)
print('Test 5 - len:', len(d6), 'items:', list(d6.items()))

d7 = MultiDict()
d7.merge({'a': 1}, a=2)
print('Test 6 (merge) - len:', len(d7), 'items:', list(d7.items()))
