# Copyright: See the LICENSE file.

from unittest import TestCase

from factory import Factory, Transformer


class TransformCounter:
    calls_count = 0

    @classmethod
    def __call__(cls, x):
        cls.calls_count += 1
        return x.upper()

    @classmethod
    def reset(cls):
        cls.calls_count = 0


transform = TransformCounter()


class Upper:
    def __init__(self, name):
        self.name = name


class UpperFactory(Factory):
    name = Transformer(transform, "value")

    class Meta:
        model = Upper


class TransformerTest(TestCase):
    def setUp(self):
        transform.reset()

    def test_transform_count(self):
        self.assertEqual("VALUE", UpperFactory().name)
        self.assertEqual(transform.calls_count, 1)

    def test_transform_kwarg(self):
        self.assertEqual("TEST", UpperFactory(name="test").name)
        self.assertEqual(transform.calls_count, 1)
