import sys
sys.path.insert(0, '.')
import multidict

print("Python version:", sys.version)
print("Multidict C extension loaded:", multidict._multidict.__file__ if hasattr(multidict, '_multidict') else "No")

md = multidict.MultiDict()
print("getall('missing'):", md.getall('missing'))
print("getall('missing', 'default'):", md.getall('missing', 'default'))
print("getall('missing', None):", md.getall('missing', None))

md.add('key', 'val1')
md.add('key', 'val2')
print("getall('key'):", md.getall('key'))
print("getall('key', 'default'):", md.getall('key', 'default'))
