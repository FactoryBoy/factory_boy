# Copyright: See the LICENSE file.

"""Helper to test circular factory dependencies."""

import factory


class Bar:
    def __init__(self, foo, y):
        self.foo = foo
        self.y = y


class BarFactory(factory.Factory):
    class Meta:
        model = Bar

    y = 13
    foo = factory.SubFactory('cyclic.foo.FooFactory')
