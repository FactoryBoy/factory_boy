# Copyright: See the LICENSE file.

"""Helper to test circular factory dependencies."""

import factory


class TreeElement:
    def __init__(self, name, parent):
        self.parent = parent
        self.name = name


class TreeElementFactory(factory.Factory):
    class Meta:
        model = TreeElement

    name = factory.Sequence(lambda n: "tree%s" % n)
    parent = factory.SubFactory('tests.cyclic.self_ref.TreeElementFactory')
