# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

"""Compatibility tools for tests"""

import sys

is_python2 = (sys.version_info[0] == 2)

if is_python2:
    import StringIO as io
else:
    import io  # noqa: F401

if sys.version_info[0:2] < (3, 3):
    import mock
else:
    from unittest import mock  # noqa: F401
