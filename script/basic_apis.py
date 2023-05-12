try:
  from collections.abc import Iterable
except ImportError:
  from collections import Iterable

def flatten(items):
  for item in items:
    if isinstance(item, Iterable) and not isinstance(item, str):
      for subitem in flatten(item):
        yield subitem
    else:
      yield item

def extend(items):
  return [item for item in flatten(items=items)]
