# Copyright: See the LICENSE file.

"""Helper to test circular factory dependencies."""

import factory

from . import bar as bar_mod


class Foo:
    def __init__(self, bar, x):
        self.bar = bar
        self.x = x


class FooFactory(factory.Factory):
    class Meta:
        model = Foo

    x = 42
    bar = factory.SubFactory(bar_mod.BarFactory)
