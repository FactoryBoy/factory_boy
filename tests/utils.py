# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2013 Raphaël Barrois
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


class MultiModulePatcher(object):
    """An abstract context processor for patching multiple modules."""

    replaced_symbol = None
    replaced_symbol_module = None
    module_imported_as = ''

    def __init__(self, *target_modules, **kwargs):
        super(MultiModulePatcher, self).__init__(**kwargs)
        if not self.module_imported_as:
            self.module_imported_as = replaced_symbol.__module__.__name__
        self.patchers = [self._build_patcher(mod) for mod in target_modules]

    def _check_module(self, target_module):
        if not self.replaced_symbol_module:
            # No check to perform
            return

        replaced_import = getattr(target_module, self.module_imported_as)
        assert replaced_import is self.replaced_symbol_module, (
            "Cannot patch import %s.%s (%r != %r)" % (
                target_module.__name__, self.module_imported_as,
                replaced_import, self.replaced_symbol_module))

    def _build_patcher(self, target_module):
        """Build a mock patcher for the target module."""
        self._check_module(target_module)

        return mock.patch.object(
            getattr(target_module, self.module_imported_as),
            self.replaced_symbol.__name__,
            mock.Mock(wraps=self.replaced_symbol),
        )

    def setup_mocked_symbol(self, mocked_symbol):
        """Setup a mocked symbol for later use."""
        pass

    def __enter__(self):
        for patcher in self.patchers:
            mocked_symbol = patcher.start()
            self.setup_mocked_symbol(mocked_symbol)

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for patcher in self.patchers:
            patcher.stop()


class mocked_date_today(MultiModulePatcher):
    """A context processor changing the value of date.today()."""
    replaced_symbol = datetime.date
    replaced_symbol_module = datetime
    module_imported_as = 'datetime'

    def __init__(self, target_date, *target_modules, **kwargs):
        self.target_date = target_date
        super(mocked_date_today, self).__init__(*target_modules, **kwargs)

    def setup_mocked_symbol(self, mocked_date):
        mocked_date.today.return_value = self.target_date


class mocked_datetime_now(MultiModulePatcher):
    replaced_symbol = datetime.datetime
    replaced_symbol_module = datetime
    module_imported_as = 'datetime'

    def __init__(self, target_dt, *target_modules, **kwargs):
        self.target_dt = target_dt
        super(mocked_datetime_now, self).__init__(*target_modules, **kwargs)

    def setup_mocked_symbol(self, mocked_datetime):
        mocked_datetime.now.return_value = self.target_dt
