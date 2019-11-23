# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

"""Compatibility tools for tests"""

import sys

is_python2 = (sys.version_info[0] == 2)

if is_python2:
    import StringIO as io
    import mock
else:
    import io  # noqa: F401
    from unittest import mock  # noqa: F401
