"""Auto factory for Fireo models."""
from typing import Type

from faker import config
from fireo import fields
from fireo.models import Model

import factory
from factory.base import (
    FactoryMetaClass,
    FactoryOptions,
    OptionDefault,
    resolve_attribute,
)
from factory.declarations import BaseDeclaration


class FireoFactory(factory.Factory):
    """Factory for mogo objects."""

    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, **kwargs):
        instance = model_class()
        for key, value in kwargs.items():
            setattr(instance, key, value)

        return instance

    @classmethod
    def _create(cls, model_class, **kwargs):
        instance = model_class()
        for key, value in kwargs.items():
            setattr(instance, key, value)

        if instance.collection_name:
            instance.save()

        return instance


class FireoAutoFactoryOptions(FactoryOptions):
    def _build_default_options(self):
        return super()._build_default_options() + [
            OptionDefault('extra_mapping', {}, inherit=True),
            OptionDefault('sub_factories', {}, inherit=True),
            OptionDefault('nested_factory_cls', None, inherit=True),
        ]


class FireoAutoFactoryMetaClass(FactoryMetaClass):
    def __new__(mcs, name, bases, attrs):
        meta_cls = attrs.get('Meta')
        model = getattr(meta_cls, 'model', None)
        if model is not None:
            base_meta = resolve_attribute('_meta', bases)
            extra_mapping = getattr(meta_cls, 'extra_mapping', getattr(base_meta, 'extra_mapping', {}))
            sub_factories = getattr(meta_cls, 'sub_factories', getattr(base_meta, 'sub_factories', {}))
            nested_factory_cls = mcs._get_nested_factory_cls(base_meta, bases, meta_cls)

            gen_attrs = FireoAutoFactoryMaker(
                sub_factories,
                extra_mapping,
                nested_factory_cls,  # type: ignore
            ).generate_factory_fields(
                model,
                attrs,
            )
            attrs.update(gen_attrs)

        cls = super().__new__(mcs, name, bases, attrs)
        return cls

    @staticmethod
    def _get_nested_factory_cls(base_meta, bases, meta_cls):
        nested_factory_cls = getattr(meta_cls, 'nested_factory_cls', getattr(base_meta, 'nested_factory_cls', None))
        if not nested_factory_cls:
            if len(bases) != 1:
                raise ValueError('You must specify nested_factory_cls in Meta if you have multiple bases')

            nested_factory_cls = bases[0]

        if not nested_factory_cls._meta.abstract:
            raise ValueError('nested_factory_cls must be abstract')

        if not issubclass(nested_factory_cls, FireoAutoFactory):
            raise ValueError('nested_factory_cls must be a FireoAutoFactory')

        return nested_factory_cls


class FireoAutoFactory(FireoFactory, metaclass=FireoAutoFactoryMetaClass):
    """Auto factory for Fireo models.

    This factory will generate fields for all fields in the model.
    You can override any field by defining it in the class.

    You can also specify Meta.extra_mapping to map fields to other factories.
    You can also specify Meta.sub_factories to map fields to other SubFactories.
        Note: Meta.sub_factories is populated automatically by the factory for not specified fields.
    You can also specify Meta.nested_factory_cls to use as a base for nested factories.

    Example:
        >>> class Comment(Model):
        ...     text = fields.TextField()
        >>>
        >>> class User(Model):
        ...     name = fields.TextField()
        ...     email = MyCustomEmailField()
        ...     comments = fields.ListField(Comment)
        >>>
        >>> class UserFactory(FireoAutoFactory):
        ...     class Meta:
        ...         model = User
        ...         extra_mapping = {
        ...             MyCustomEmailField: factory.Faker('email'),
        ...         }
        >>>
        >>> model = UserFactory.create()
        >>> assert model.name
        >>> assert model.email # works for custom fields too
        >>> assert model.comments[0].text  # works for nested models too
    """
    _options_class = FireoAutoFactoryOptions

    class Meta:
        abstract = True


def _raise_not_implemented(*_, **__):
    raise NotImplementedError()


def nullable(field, factory_field):
    if not field.raw_attributes.get('required'):
        factory_field = MaybeNone(factory_field)

    return factory_field


class FireoAutoFactoryMaker:
    mapping = {
        fields.IDField: lambda maker, field: nullable(field, factory.Faker('pystr', min_chars=20, max_chars=20)),
        fields.BooleanField: lambda maker, field: nullable(field, factory.Faker('pybool')),
        fields.DateTime: lambda maker, field: nullable(field, factory.Faker('date_time')),
        fields.NumberField: lambda maker, field: nullable(field, (
            factory.Faker('pyint')
            if field.raw_attributes.get('int_only') else
            factory.Faker('pyfloat')
        )),
        fields.TextField: lambda maker, field: nullable(field, factory.Faker('pystr')),
        fields.MapField: lambda maker, field: nullable(field, factory.Faker('pydict', value_types=[str])),
        fields.ReferenceField: _raise_not_implemented,
        fields.GeoPoint: _raise_not_implemented,
        fields.Field: _raise_not_implemented,
        fields.ListField: lambda maker, field: nullable(field, (
            factory.Faker('pylist', value_types=[str])
            if field.raw_attributes.get('nested_field') is None else
            factory.List([maker.get_field_factory(field.raw_attributes['nested_field'])])
        )),
        fields.NestedModelField: lambda maker, field: nullable(
            field, factory.SubFactory(maker.get_model_factory(field.nested_model))
        ),
    }

    def __init__(
        self,
        sub_factories: dict[Model, Type[FireoFactory]] | None = None,
        extra_mapping: None = None,
        base_cls: Type[FireoAutoFactory] = FireoAutoFactory,  # type: ignore
    ):
        self.sub_factories = sub_factories or {}
        self.mapping = {
            **self.mapping,
            **(extra_mapping or {}),
        }
        self.base_cls = base_cls

    def get_field_factory(self, field: fields.Field) -> BaseDeclaration:
        field_type = type(field)
        if field_type in self.mapping:
            return self.mapping[field_type](self, field)  # type: ignore
        else:
            raise NotImplementedError(f'Field type {field_type} is not implemented')

    def get_model_factory(self, model: Model):
        if model not in self.sub_factories:
            the_model = model

            class AutoFactory(self.base_cls):  # type: ignore
                class Meta:
                    model = the_model

            AutoFactory.__name__ = f'{model.__name__}Factory'
            self.sub_factories[model] = AutoFactory

        return self.sub_factories[model]

    def generate_factory_fields(self, model: Model, attrs: dict) -> dict[str, BaseDeclaration]:
        generated_fields = {}
        for field_name, field in model._meta.field_list.items():
            if field_name in attrs:
                continue

            if not isinstance(field, fields.Field):
                continue

            generated_fields[field_name] = self.get_field_factory(field)

        return generated_fields


class MaybeNone(factory.Maybe):
    """Factory for optional fields."""

    def __init__(self, field):
        super().__init__(factory.Faker("boolean", locale=config.DEFAULT_LOCALE), field, None)

    def evaluate_pre(self, instance, step, overrides):
        choice = self.decider.evaluate(instance=instance, step=step, extra={
            'locale': config.DEFAULT_LOCALE,
        })
        target = self.yes if choice else self.no

        if isinstance(target, BaseDeclaration):
            return target.evaluate_pre(
                instance=instance,
                step=step,
                overrides=overrides,
            )
        else:
            # Flat value (can't be POST_INSTANTIATION, checked in __init__)
            return target
