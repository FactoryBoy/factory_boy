# -*- coding: utf-8 -*-
import sys
PY3 = sys.version_info[0] == 3

def with_metaclass(meta, base=object):
    """Create a base class with a metaclass."""
    return meta("NewBase", (base,), {})