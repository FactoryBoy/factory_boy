# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

"""Compatibility tools for tests"""

import sys

is_python2 = (sys.version_info[0] == 2)

if sys.version_info[0:2] < (2, 7):  # pragma: no cover
    import unittest2 as unittest
else:  # pragma: no cover
    import unittest

if sys.version_info[0] == 2:  # pragma: no cover
    import StringIO as io
else:  # pragma: no cover
    import io

if sys.version_info[0:2] < (3, 3):  # pragma: no cover
    import mock
else:  # pragma: no cover
    from unittest import mock

