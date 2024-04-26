import unittest
from typing import List, Optional, Union

from fireo.typedmodels import TypedModel

import factory
from factory.fireo import FireoAutoFactory, MaybeNone


class Deep1Model(TypedModel):
    nested_int: int


class RootModel(TypedModel):
    int_: int
    float_: float
    str_: str
    bool_: bool
    list_: list
    dict_: dict
    int_or_float: Union[int, float]
    optional_int_or_float: Union[int, float, None]
    optional_int: Optional[int]
    list_of_int: List[int]
    list_of_int_or_none: List[Optional[int]]
    none_or_list_of_int: Optional[List[int]]

    nested: Deep1Model
    list_of_nested: List[Deep1Model]


class RootModelFactory(FireoAutoFactory):
    class Meta:
        model = RootModel


class FireoAutoFactoryTestCase(unittest.TestCase):
    def test_generate_fields_by_auto_factory(self):
        assert RootModelFactory.int_.provider == 'pyint'
        assert RootModelFactory.float_.provider == 'pyfloat'
        assert RootModelFactory.str_.provider == 'pystr'
        assert RootModelFactory.bool_.provider == 'pybool'
        assert RootModelFactory.list_.provider == 'pylist'
        assert RootModelFactory.dict_.provider == 'pydict'
        assert RootModelFactory.int_or_float.provider == 'pyfloat'

        assert RootModelFactory.optional_int_or_float.__class__ is MaybeNone
        assert RootModelFactory.optional_int_or_float.yes.provider == 'pyfloat'

        assert RootModelFactory.optional_int.__class__ is MaybeNone
        assert RootModelFactory.optional_int.yes.provider == 'pyint'

        assert RootModelFactory.list_of_int.__class__ is factory.List
        assert RootModelFactory.list_of_int._defaults['0'].provider == 'pyint'

        assert RootModelFactory.list_of_int_or_none.__class__ == factory.List
        assert RootModelFactory.list_of_int_or_none._defaults['0'].__class__ is MaybeNone
        assert RootModelFactory.list_of_int_or_none._defaults['0'].yes.provider == 'pyint'

        assert RootModelFactory.none_or_list_of_int.__class__ is MaybeNone
        assert RootModelFactory.none_or_list_of_int.yes.__class__ is factory.List
        assert RootModelFactory.none_or_list_of_int.yes._defaults['0'].provider == 'pyint'

        assert RootModelFactory.nested.__class__ is factory.SubFactory
        deep1_model_factory = RootModelFactory.nested.factory_wrapper.factory
        assert deep1_model_factory.__name__ == 'Deep1ModelFactory'
        assert RootModelFactory.nested.factory_wrapper.factory._meta.model is Deep1Model
        assert deep1_model_factory.nested_int.provider == 'pyint'

        assert RootModelFactory.list_of_nested.__class__ is factory.List
        assert RootModelFactory.list_of_nested._defaults['0'].__class__ is factory.SubFactory
        assert RootModelFactory.list_of_nested._defaults['0'].factory_wrapper.factory is deep1_model_factory

    def test_generate_model_by_auto_factory(self):
        model = RootModelFactory.build()

        assert isinstance(model, RootModel)
        assert isinstance(model.int_, int)
        assert isinstance(model.float_, float)
        assert isinstance(model.str_, str)
        assert isinstance(model.bool_, bool)
        assert isinstance(model.list_, list)
        assert isinstance(model.dict_, dict)
        assert isinstance(model.int_or_float, (int, float))
        assert isinstance(model.optional_int_or_float, (int, float, type(None)))
        assert isinstance(model.optional_int, (int, type(None)))
        assert isinstance(model.list_of_int, list)
        assert all(isinstance(i, int) for i in model.list_of_int)
        assert isinstance(model.list_of_int_or_none, list)
        assert all(isinstance(i, (int, type(None))) for i in model.list_of_int_or_none)
        assert isinstance(model.nested, Deep1Model)
        assert isinstance(model.nested.nested_int, int)
        assert isinstance(model.list_of_nested, list)
        assert all(isinstance(i, Deep1Model) for i in model.list_of_nested)
        assert all(isinstance(i.nested_int, int) for i in model.list_of_nested)
