# Copyright: See the LICENSE file.

import functools
import warnings

import factory

from . import alter_time


def disable_warnings(fun):
    @functools.wraps(fun)
    def decorated(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return fun(*args, **kwargs)
    return decorated


class MultiModulePatcher:
    """An abstract context processor for patching multiple modules."""

    def __init__(self, *target_modules, **kwargs):
        super().__init__(**kwargs)
        self.patchers = [self._build_patcher(mod) for mod in target_modules]

    def _build_patcher(self, target_module):  # pragma: no cover
        """Build a mock patcher for the target module."""
        raise NotImplementedError()

    def __enter__(self):
        for patcher in self.patchers:
            patcher.start()

    def __exit__(self, exc_type=None, exc_val=None, exc_tb=None):
        for patcher in self.patchers:
            patcher.stop()


class mocked_date_today(MultiModulePatcher):
    """A context processor changing the value of date.today()."""

    def __init__(self, target_date, *target_modules, **kwargs):
        self.target_date = target_date
        super().__init__(*target_modules, **kwargs)

    def _build_patcher(self, target_module):
        module_datetime = getattr(target_module, 'datetime')
        return alter_time.mock_date_today(self.target_date, module_datetime)


class mocked_datetime_now(MultiModulePatcher):
    def __init__(self, target_dt, *target_modules, **kwargs):
        self.target_dt = target_dt
        super().__init__(*target_modules, **kwargs)

    def _build_patcher(self, target_module):
        module_datetime = getattr(target_module, 'datetime')
        return alter_time.mock_datetime_now(self.target_dt, module_datetime)


def evaluate_declaration(declaration, force_sequence=None):
    kwargs = {'attr': declaration}
    if force_sequence is not None:
        kwargs['__sequence'] = force_sequence

    return factory.build(dict, **kwargs)['attr']
