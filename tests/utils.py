# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2015 Raphaël Barrois
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import datetime

from .compat import mock
from . import alter_time


class MultiModulePatcher(object):
    """An abstract context processor for patching multiple modules."""

    def __init__(self, *target_modules, **kwargs):
        super(MultiModulePatcher, self).__init__(**kwargs)
        self.patchers = [self._build_patcher(mod) for mod in target_modules]

    def _build_patcher(self, target_module):  # pragma: no cover
        """Build a mock patcher for the target module."""
        raise NotImplementedError()

    def __enter__(self):
        for patcher in self.patchers:
            mocked_symbol = patcher.start()

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for patcher in self.patchers:
            patcher.stop()


class mocked_date_today(MultiModulePatcher):
    """A context processor changing the value of date.today()."""

    def __init__(self, target_date, *target_modules, **kwargs):
        self.target_date = target_date
        super(mocked_date_today, self).__init__(*target_modules, **kwargs)

    def _build_patcher(self, target_module):
        module_datetime = getattr(target_module, 'datetime')
        return alter_time.mock_date_today(self.target_date, module_datetime)


class mocked_datetime_now(MultiModulePatcher):
    def __init__(self, target_dt, *target_modules, **kwargs):
        self.target_dt = target_dt
        super(mocked_datetime_now, self).__init__(*target_modules, **kwargs)

    def _build_patcher(self, target_module):
        module_datetime = getattr(target_module, 'datetime')
        return alter_time.mock_datetime_now(self.target_dt, module_datetime)
