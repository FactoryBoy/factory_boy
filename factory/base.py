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

import collections
import logging

from . import containers
from . import declarations
from . import utils

logger = logging.getLogger('factory.generate')

# Strategies
BUILD_STRATEGY = 'build'
CREATE_STRATEGY = 'create'
STUB_STRATEGY = 'stub'



class FactoryError(Exception):
    """Any exception raised by factory_boy."""


class AssociatedClassError(FactoryError):
    """Exception for Factory subclasses lacking Meta.model."""


class UnknownStrategy(FactoryError):
    """Raised when a factory uses an unknown strategy."""


class UnsupportedStrategy(FactoryError):
    """Raised when trying to use a strategy on an incompatible Factory."""


# Factory metaclasses

def get_factory_bases(bases):
    """Retrieve all FactoryMetaClass-derived bases from a list."""
    return [b for b in bases if issubclass(b, BaseFactory)]


def resolve_attribute(name, bases, default=None):
    """Find the first definition of an attribute according to MRO order."""
    for base in bases:
        if hasattr(base, name):
            return getattr(base, name)
    return default


class FactoryMetaClass(type):
    """Factory metaclass for handling ordered declarations."""

    def __call__(cls, **kwargs):
        """Override the default Factory() syntax to call the default strategy.

        Returns an instance of the associated class.
        """

        if cls._meta.strategy == BUILD_STRATEGY:
            return cls.build(**kwargs)
        elif cls._meta.strategy == CREATE_STRATEGY:
            return cls.create(**kwargs)
        elif cls._meta.strategy == STUB_STRATEGY:
            return cls.stub(**kwargs)
        else:
            raise UnknownStrategy('Unknown Meta.strategy: {0}'.format(
                cls._meta.strategy))

    def __new__(mcs, class_name, bases, attrs):
        """Record attributes as a pattern for later instance construction.

        This is called when a new Factory subclass is defined; it will collect
        attribute declaration from the class definition.

        Args:
            class_name (str): the name of the class being created
            bases (list of class): the parents of the class being created
            attrs (str => obj dict): the attributes as defined in the class
                definition

        Returns:
            A new class
        """
        parent_factories = get_factory_bases(bases)
        if parent_factories:
            base_factory = parent_factories[0]
        else:
            base_factory = None

        attrs_meta = attrs.pop('Meta', None)

        base_meta = resolve_attribute('_meta', bases)
        options_class = resolve_attribute('_options_class', bases, FactoryOptions)

        meta = options_class()
        attrs['_meta'] = meta

        new_class = super(FactoryMetaClass, mcs).__new__(
            mcs, class_name, bases, attrs)

        meta.contribute_to_class(new_class,
            meta=attrs_meta,
            base_meta=base_meta,
            base_factory=base_factory,
        )

        return new_class

    def __str__(cls):
        if cls._meta.abstract:
            return '<%s (abstract)>' % cls.__name__
        else:
            return '<%s for %s>' % (cls.__name__, cls._meta.model)


class BaseMeta:
    abstract = True
    strategy = CREATE_STRATEGY


class OptionDefault(object):
    """Simple manager to handle default options.

    The goal of this class is to make it easy to declare options
    for a ``class Meta``.

    Args:
        name (str): the name of the option
        default_value: the default value
        inherit (bool): whether to pick defined values from a parent
        merger (callable or None): how to merge the new value and the inherited one.
            Mostly useful when the value is a dict
    """

    def __init__(self, name, default_value, inherit=False, merger=None):
        self.name = name
        self.default_value = default_value
        self.inherit = inherit
        if merger is not None and not inherit:
            raise ValueError("A merger should only be provided to inheritable OptionDefault.")
        self.merger = merger

    def apply(self, meta, base_meta):
        """Compute the option value based on the new meta class and the parent one."""
        class EMPTY:
            pass

        old_value = EMPTY
        new_value = EMPTY
        if self.inherit and base_meta is not None:
            old_value = getattr(base_meta, self.name, EMPTY)
        if meta is not None:
            new_value = getattr(meta, self.name, EMPTY)

        if old_value is EMPTY:
            if new_value is EMPTY:
                return self.default_value
            else:
                return new_value
        else:
            if new_value is EMPTY:
                return old_value
            elif self.merger is not None:
                # We have an old value and a new value; use the merger.
                return self.merger(old=old_value, new=new_value)
            else:
                return new_value

    def __str__(self):
        return '%s(%r, %r, inherit=%r)' % (
            self.__class__.__name__,
            self.name, self.default_value, self.inherit)

    @staticmethod
    def dict_merge(old, new):
        """Simple merger for dictionaries."""
        result = {}
        result.update(old)
        result.update(new)
        return result


FieldContext = collections.namedtuple('FieldContext',
    ['field', 'field_name', 'model', 'factory', 'skips'])


class BaseIntrospector(object):
    """Introspector for models.

    Extracts declarations from a model.

    Attributes:
        DEFAULT_BUILDERS ((field_class, callable) list): maps a field_class
            to a callable able to build a declaration from it
    """

    DEFAULT_BUILDERS = []

    def __init__(self, factory_class):
        # Don't use a dict as DEFAULT_BUILDERS to avoid issues
        # when inheriting an Introspector.
        self.builders = dict(self.DEFAULT_BUILDERS)
        self._factory_class = factory_class
        self._model = self._factory_class._meta.model

    def get_field_names(self, model):
        """Fetch all "auto-declarable" field names from a model."""
        raise NotImplementedError("Introspector %r doesn't know how to extract fields from %s" % (self, model))

    def get_field_by_name(self, model, field_name):
        """Get the actual "field descriptor" for a given field name"""
        raise NotImplementedError("Introspector %r doesn't know how to fetch field %s from %r"
            % (self._factory_class, field_name, model))

    def build_declaration(self, field_name, field, sub_skips):
        """Build a factory.Declaration from a field_name/field combination.

        Relies on ``self.DEFAULT_BUILDERS``.

        Returns:
            factory.Declaration or None.
        """
        if field.__class__ not in self.builders:
            raise NotImplementedError(
                    "Introspector %r lacks recipe for building field %r; add it to %s.Meta.auto_fields_rules."
                    % (self, field, self._factory_class.__name__))
        field_ctxt = FieldContext(
            field=field,
            field_name=field_name,
            model=self._model,
            factory=self._factory_class,
            skips=sub_skips,
        )
        builder = self.builders[field.__class__]
        return builder(field_ctxt)

    def build_declarations(self, for_fields, skip_fields=()):
        """Build declarations for a set of fields.

        Args:
            for_fields (str iterable): list of fields to build (can be '*' to build all fields)
            skip_fields (str iterable): list of fields that should *NOT* be built.

        Returns:
            (str, factory.Declaration) list: the new declarations.
        """
        if '*' in for_fields:
            if len(for_fields) != 1:
                raise ValueError("If %s._meta.auto_fields contains '*', it cannot contain other values; found %r."
                    % (for_fields, self._factory_class))
            for_fields = self.get_field_names(self._model)
        
        declarations = {}
        for field_name in for_fields:
            if field_name in skip_fields:
                continue

            sub_skip_pattern = '%s__' % field_name
            sub_skips = [
                sk[len(sub_skip_pattern):]
                for sk in skip_fields
                if sk.startswith(sub_skip_pattern)
            ]

            field = self.get_field_by_name(self._model, field_name)
            declaration = self.build_declaration(field_name, field, sub_skips)
            if declaration is not None:
                declarations[field_name] = declaration

        return declarations

    def __repr__(self):
        return '<%s for %s>' % (self.__class__.__name__, self._factory_class.__name__)


class FactoryOptions(object):
    DEFAULT_INTROSPECTOR_CLASS = BaseIntrospector

    def __init__(self):
        self.factory = None
        self.base_factory = None
        self.declarations = {}
        self.postgen_declarations = {}
        self.introspector = None

    def _build_default_options(self):
        """"Provide the default value for all allowed fields.

        Custom FactoryOptions classes should override this method
        to update() its return value.
        """
        return [
            # The model this factory build
            OptionDefault('model', None, inherit=True),
            # Whether this factory is allowed to build objects
            OptionDefault('abstract', False, inherit=False),
            # The default strategy (BUILD_STRATEGY or CREATE_STRATEGY)
            OptionDefault('strategy', CREATE_STRATEGY, inherit=True),
            # Declarations that should be passed as *args instead
            OptionDefault('inline_args', (), inherit=True),
            # Declarations that shouldn't be passed to the object
            OptionDefault('exclude', (), inherit=True),
            # Declarations that should be used under another name
            # to the target model (for name conflict handling)
            OptionDefault('rename', {}, inherit=True),
            # The introspector class to use; if None (the default),
            # uses self.DEFAULT_INTROSPECTOR_CLASS
            OptionDefault('introspector_class', None, inherit=True),
            # The list of fields to auto-generate
            OptionDefault('auto_fields', (), inherit=False),
        ]

    def _fill_from_meta(self, meta, base_meta):
        # Exclude private/protected fields from the meta
        if meta is None:
            meta_attrs = {}
        else:
            meta_attrs = dict((k, v)
                for (k, v) in vars(meta).items()
                if not k.startswith('_')
            )

        for option in self._build_default_options():
            assert not hasattr(self, option.name), "Can't override field %s." % option.name
            value = option.apply(meta, base_meta)
            meta_attrs.pop(option.name, None)
            setattr(self, option.name, value)

        if meta_attrs:
            # Some attributes in the Meta aren't allowed here
            raise TypeError("'class Meta' for %r got unknown attribute(s) %s"
                    % (self.factory, ','.join(sorted(meta_attrs.keys()))))

    def contribute_to_class(self, factory,
            meta=None, base_meta=None, base_factory=None):

        self.factory = factory
        self.base_factory = base_factory

        self._fill_from_meta(meta=meta, base_meta=base_meta)

        if self.introspector_class is None:
            # Due to OptionDefault inheritance handling,
            # we don't want to set self.introspector_class
            # as that would break the default.
            self.introspector = self.DEFAULT_INTROSPECTOR_CLASS(factory)
        else:
            self.introspector = self.introspector_class(factory)

        self.model = self.factory._load_model_class(self.model)
        if self.model is None:
            self.abstract = True

        self.counter_reference = self._get_counter_reference()

        for parent in reversed(self.factory.__mro__[1:]):
            if not hasattr(parent, '_meta'):
                continue
            self.declarations.update(parent._meta.declarations)
            self.postgen_declarations.update(parent._meta.postgen_declarations)

        raw_declarations = dict(vars(self.factory))
        auto_declarations = self.introspector.build_declarations(
            for_fields=self.auto_fields,
            skip_fields=raw_declarations.keys(),
        )
        raw_declarations.update(auto_declarations)

        for k, v in raw_declarations.items():
            if self._is_declaration(k, v):
                self.declarations[k] = v
            if self._is_postgen_declaration(k, v):
                self.postgen_declarations[k] = v

    def _get_counter_reference(self):
        """Identify which factory should be used for a shared counter."""

        if (self.model is not None
                and self.base_factory is not None
                and self.base_factory._meta.model is not None
                and issubclass(self.model, self.base_factory._meta.model)):
            return self.base_factory
        else:
            return self.factory

    def _is_declaration(self, name, value):
        """Determines if a class attribute is a field value declaration.

        Based on the name and value of the class attribute, return ``True`` if
        it looks like a declaration of a default field value, ``False`` if it
        is private (name starts with '_') or a classmethod or staticmethod.

        """
        if isinstance(value, (classmethod, staticmethod)):
            return False
        elif isinstance(value, declarations.OrderedDeclaration):
            return True
        elif isinstance(value, declarations.PostGenerationDeclaration):
            return False
        return not name.startswith("_")

    def _is_postgen_declaration(self, name, value):
        """Captures instances of PostGenerationDeclaration."""
        return isinstance(value, declarations.PostGenerationDeclaration)

    def __str__(self):
        return "<%s for %s>" % (self.__class__.__name__, self.factory.__class__.__name__)

    def __repr__(self):
        return str(self)


# Factory base classes


class _Counter(object):
    """Simple, naive counter.

    Attributes:
        for_class (obj): the class this counter related to
        seq (int): the next value
    """

    def __init__(self, seq, for_class):
        self.seq = seq
        self.for_class = for_class

    def next(self):
        value = self.seq
        self.seq += 1
        return value

    def reset(self, next_value=0):
        self.seq = next_value

    def __repr__(self):
        return '<_Counter for %s.%s, next=%d>' % (
            self.for_class.__module__, self.for_class.__name__, self.seq)


class BaseFactory(object):
    """Factory base support for sequences, attributes and stubs."""

    # Backwards compatibility
    UnknownStrategy = UnknownStrategy
    UnsupportedStrategy = UnsupportedStrategy

    def __new__(cls, *args, **kwargs):
        """Would be called if trying to instantiate the class."""
        raise FactoryError('You cannot instantiate BaseFactory')

    _meta = FactoryOptions()

    # ID to use for the next 'declarations.Sequence' attribute.
    _counter = None

    @classmethod
    def reset_sequence(cls, value=None, force=False):
        """Reset the sequence counter.

        Args:
            value (int or None): the new 'next' sequence value; if None,
                recompute the next value from _setup_next_sequence().
            force (bool): whether to force-reset parent sequence counters
                in a factory inheritance chain.
        """
        if cls._meta.counter_reference is not cls:
            if force:
                cls._meta.base_factory.reset_sequence(value=value)
            else:
                raise ValueError(
                    "Cannot reset the sequence of a factory subclass. "
                    "Please call reset_sequence() on the root factory, "
                    "or call reset_sequence(force=True)."
                )
        else:
            cls._setup_counter()
            if value is None:
                value = cls._setup_next_sequence()
            cls._counter.reset(value)

    @classmethod
    def _setup_next_sequence(cls):
        """Set up an initial sequence value for Sequence attributes.

        Returns:
            int: the first available ID to use for instances of this factory.
        """
        return 0

    @classmethod
    def _setup_counter(cls):
        """Ensures cls._counter is set for this class.

        Due to the way inheritance works in Python, we need to ensure that the
        ``_counter`` attribute has been initialized for *this* Factory subclass,
        not one of its parents.
        """
        if cls._counter is None or cls._counter.for_class != cls:
            first_seq = cls._setup_next_sequence()
            cls._counter = _Counter(for_class=cls, seq=first_seq)
            logger.debug("%r: Setting up next sequence (%d)", cls, first_seq)

    @classmethod
    def _generate_next_sequence(cls):
        """Retrieve a new sequence ID.

        This will call, in order:
        - _generate_next_sequence from the base factory, if provided
        - _setup_next_sequence, if this is the 'toplevel' factory and the
            sequence counter wasn't initialized yet; then increase it.
        """

        # Rely upon our parents
        if cls._meta.counter_reference is not cls:
            logger.debug("%r: reusing sequence from %r", cls, cls._meta.base_factory)
            return cls._meta.base_factory._generate_next_sequence()

        # Make sure _counter is initialized
        cls._setup_counter()

        # Pick current value, then increase class counter for the next call.
        return cls._counter.next()

    @classmethod
    def attributes(cls, create=False, extra=None):
        """Build a dict of attribute values, respecting declaration order.

        The process is:
        - Handle 'orderless' attributes, overriding defaults with provided
            kwargs when applicable
        - Handle ordered attributes, overriding them with provided kwargs when
            applicable; the current list of computed attributes is available
            to the currently processed object.
        """
        force_sequence = None
        if extra:
            force_sequence = extra.pop('__sequence', None)
        log_ctx = '%s.%s' % (cls.__module__, cls.__name__)
        logger.debug('BaseFactory: Preparing %s.%s(extra=%r)',
            cls.__module__,
            cls.__name__,
            extra,
        )
        return containers.AttributeBuilder(cls, extra, log_ctx=log_ctx).build(
            create=create,
            force_sequence=force_sequence,
        )

    @classmethod
    def declarations(cls, extra_defs=None):
        """Retrieve a copy of the declared attributes.

        Args:
            extra_defs (dict): additional definitions to insert into the
                retrieved DeclarationDict.
        """
        decls = cls._meta.declarations.copy()
        decls.update(extra_defs or {})
        return decls

    @classmethod
    def _rename_fields(cls, **kwargs):
        for old_name, new_name in cls._meta.rename.items():
            kwargs[new_name] = kwargs.pop(old_name)
        return kwargs

    @classmethod
    def _adjust_kwargs(cls, **kwargs):
        """Extension point for custom kwargs adjustment."""
        return kwargs

    @classmethod
    def _load_model_class(cls, class_definition):
        """Extension point for loading model classes.

        This can be overridden in framework-specific subclasses to hook into
        existing model repositories, for instance.
        """
        return class_definition

    @classmethod
    def _get_model_class(cls):
        """Retrieve the actual, associated model class."""
        definition = cls._meta.model
        return cls._load_model_class(definition)

    @classmethod
    def _prepare(cls, create, **kwargs):
        """Prepare an object for this factory.

        Args:
            create: bool, whether to create or to build the object
            **kwargs: arguments to pass to the creation function
        """
        model_class = cls._get_model_class()
        kwargs = cls._rename_fields(**kwargs)
        kwargs = cls._adjust_kwargs(**kwargs)

        # Remove 'hidden' arguments.
        for arg in cls._meta.exclude:
            del kwargs[arg]

        # Extract *args from **kwargs
        args = tuple(kwargs.pop(key) for key in cls._meta.inline_args)

        logger.debug('BaseFactory: Generating %s.%s(%s)',
            cls.__module__,
            cls.__name__,
            utils.log_pprint(args, kwargs),
        )
        if create:
            return cls._create(model_class, *args, **kwargs)
        else:
            return cls._build(model_class, *args, **kwargs)

    @classmethod
    def _generate(cls, create, attrs):
        """generate the object.

        Args:
            create (bool): whether to 'build' or 'create' the object
            attrs (dict): attributes to use for generating the object
        """
        if cls._meta.abstract:
            raise FactoryError(
                "Cannot generate instances of abstract factory %(f)s; "
                "Ensure %(f)s.Meta.model is set and %(f)s.Meta.abstract "
                "is either not set or False." % dict(f=cls.__name__))

        # Extract declarations used for post-generation
        postgen_declarations = cls._meta.postgen_declarations
        postgen_attributes = {}
        for name, decl in sorted(postgen_declarations.items()):
            postgen_attributes[name] = decl.extract(name, attrs)

        # Generate the object
        obj = cls._prepare(create, **attrs)

        # Handle post-generation attributes
        results = {}
        for name, decl in sorted(postgen_declarations.items()):
            extraction_context = postgen_attributes[name]
            results[name] = decl.call(obj, create, extraction_context)

        cls._after_postgeneration(obj, create, results)

        return obj

    @classmethod
    def _after_postgeneration(cls, obj, create, results=None):
        """Hook called after post-generation declarations have been handled.

        Args:
            obj (object): the generated object
            create (bool): whether the strategy was 'build' or 'create'
            results (dict or None): result of post-generation declarations
        """
        pass

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        """Actually build an instance of the model_class.

        Customization point, will be called once the full set of args and kwargs
        has been computed.

        Args:
            model_class (type): the class for which an instance should be
                built
            args (tuple): arguments to use when building the class
            kwargs (dict): keyword arguments to use when building the class
        """
        return model_class(*args, **kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Actually create an instance of the model_class.

        Customization point, will be called once the full set of args and kwargs
        has been computed.

        Args:
            model_class (type): the class for which an instance should be
                created
            args (tuple): arguments to use when creating the class
            kwargs (dict): keyword arguments to use when creating the class
        """
        return model_class(*args, **kwargs)

    @classmethod
    def build(cls, **kwargs):
        """Build an instance of the associated class, with overriden attrs."""
        attrs = cls.attributes(create=False, extra=kwargs)
        return cls._generate(False, attrs)

    @classmethod
    def build_batch(cls, size, **kwargs):
        """Build a batch of instances of the given class, with overriden attrs.

        Args:
            size (int): the number of instances to build

        Returns:
            object list: the built instances
        """
        return [cls.build(**kwargs) for _ in range(size)]

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overriden attrs."""
        attrs = cls.attributes(create=True, extra=kwargs)
        return cls._generate(True, attrs)

    @classmethod
    def create_batch(cls, size, **kwargs):
        """Create a batch of instances of the given class, with overriden attrs.

        Args:
            size (int): the number of instances to create

        Returns:
            object list: the created instances
        """
        return [cls.create(**kwargs) for _ in range(size)]

    @classmethod
    def stub(cls, **kwargs):
        """Retrieve a stub of the associated class, with overriden attrs.

        This will return an object whose attributes are those defined in this
        factory's declarations or in the extra kwargs.
        """
        stub_object = containers.StubObject()
        for name, value in cls.attributes(create=False, extra=kwargs).items():
            setattr(stub_object, name, value)
        return stub_object

    @classmethod
    def stub_batch(cls, size, **kwargs):
        """Stub a batch of instances of the given class, with overriden attrs.

        Args:
            size (int): the number of instances to stub

        Returns:
            object list: the stubbed instances
        """
        return [cls.stub(**kwargs) for _ in range(size)]

    @classmethod
    def generate(cls, strategy, **kwargs):
        """Generate a new instance.

        The instance will be created with the given strategy (one of
        BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY).

        Args:
            strategy (str): the strategy to use for generating the instance.

        Returns:
            object: the generated instance
        """
        assert strategy in (STUB_STRATEGY, BUILD_STRATEGY, CREATE_STRATEGY)
        action = getattr(cls, strategy)
        return action(**kwargs)

    @classmethod
    def generate_batch(cls, strategy, size, **kwargs):
        """Generate a batch of instances.

        The instances will be created with the given strategy (one of
        BUILD_STRATEGY, CREATE_STRATEGY, STUB_STRATEGY).

        Args:
            strategy (str): the strategy to use for generating the instance.
            size (int): the number of instances to generate

        Returns:
            object list: the generated instances
        """
        assert strategy in (STUB_STRATEGY, BUILD_STRATEGY, CREATE_STRATEGY)
        batch_action = getattr(cls, '%s_batch' % strategy)
        return batch_action(size, **kwargs)

    @classmethod
    def simple_generate(cls, create, **kwargs):
        """Generate a new instance.

        The instance will be either 'built' or 'created'.

        Args:
            create (bool): whether to 'build' or 'create' the instance.

        Returns:
            object: the generated instance
        """
        strategy = CREATE_STRATEGY if create else BUILD_STRATEGY
        return cls.generate(strategy, **kwargs)

    @classmethod
    def simple_generate_batch(cls, create, size, **kwargs):
        """Generate a batch of instances.

        These instances will be either 'built' or 'created'.

        Args:
            size (int): the number of instances to generate
            create (bool): whether to 'build' or 'create' the instances.

        Returns:
            object list: the generated instances
        """
        strategy = CREATE_STRATEGY if create else BUILD_STRATEGY
        return cls.generate_batch(strategy, size, **kwargs)

    @classmethod
    def auto_factory(cls, target_model, for_fields=('*',), **field_overrides):
        """Introspect the target_model and build a factory for it.

        Args:
            target_model (type): the model for which a factory should be built
            for_fields (str list): name of fields to introspect on the model
            field_overrides (dict): extra declarations to include in the factory,
                e.g default values

        Returns:
            Factory subclass: the generated factory
        """
        factory_name = '%sAutoFactory' % target_model.__name__
        class Meta:
            model = target_model
            auto_fields = for_fields
        attrs = {}
        attrs.update(field_overrides)
        attrs['Meta'] = Meta
        # We want to force the name of the Factory subclass.
        factory_class = type(factory_name, (cls,), attrs)
        return factory_class



Factory = FactoryMetaClass('Factory', (BaseFactory,), {
    'Meta': BaseMeta,
    '__doc__': """Factory base with build and create support.

    This class has the ability to support multiple ORMs by using custom creation
    functions.
    """,
})


# Backwards compatibility
Factory.AssociatedClassError = AssociatedClassError  # pylint: disable=W0201


class StubFactory(Factory):

    class Meta:
        strategy = STUB_STRATEGY
        model = containers.StubObject

    @classmethod
    def build(cls, **kwargs):
        return cls.stub(**kwargs)

    @classmethod
    def create(cls, **kwargs):
        raise UnsupportedStrategy()


class BaseDictFactory(Factory):
    """Factory for dictionary-like classes."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        if args:
            raise ValueError(
                "DictFactory %r does not support Meta.inline_args.", cls)
        return model_class(**kwargs)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)


class DictFactory(BaseDictFactory):
    class Meta:
        model = dict


class BaseListFactory(Factory):
    """Factory for list-like classes."""
    class Meta:
        abstract = True

    @classmethod
    def _build(cls, model_class, *args, **kwargs):
        if args:
            raise ValueError(
                "ListFactory %r does not support Meta.inline_args.", cls)

        values = [v for k, v in sorted(kwargs.items())]
        return model_class(values)

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        return cls._build(model_class, *args, **kwargs)


class ListFactory(BaseListFactory):
    class Meta:
        model = list


def use_strategy(new_strategy):
    """Force the use of a different strategy.

    This is an alternative to setting default_strategy in the class definition.
    """
    def wrapped_class(klass):
        klass._meta.strategy = new_strategy
        return klass
    return wrapped_class
