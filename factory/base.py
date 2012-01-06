# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011 Raphaël Barrois
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

import re
import sys

from factory import containers

# Strategies
BUILD_STRATEGY = 'build'
CREATE_STRATEGY = 'create'
STUB_STRATEGY = 'stub'

# Creation functions. Use Factory.set_creation_function() to set a creation function appropriate for your ORM.
DJANGO_CREATION = lambda class_to_create, **kwargs: class_to_create.objects.create(**kwargs)

# Building functions. Use Factory.set_building_function() to set a building functions appropriate for your ORM.
NAIVE_BUILD = lambda class_to_build, **kwargs: class_to_build(**kwargs)
MOGO_BUILD = lambda class_to_build, **kwargs: class_to_build.new(**kwargs)


# Special declarations
FACTORY_CLASS_DECLARATION = 'FACTORY_FOR'

# Factory class attributes
CLASS_ATTRIBUTE_DECLARATIONS = '_declarations'
CLASS_ATTRIBUTE_ASSOCIATED_CLASS = '_associated_class'


# Factory metaclasses

def get_factory_bases(bases):
    """Retrieve all BaseFactoryMetaClass-derived bases from a list."""
    return [b for b in bases if isinstance(b, BaseFactoryMetaClass)]


class BaseFactoryMetaClass(type):
    """Factory metaclass for handling ordered declarations."""

    def __call__(cls, **kwargs):
        """Override the default Factory() syntax to call the default build strategy.

        Returns an instance of the associated class.
        """

        if cls.default_strategy == BUILD_STRATEGY:
            return cls.build(**kwargs)
        elif cls.default_strategy == CREATE_STRATEGY:
            return cls.create(**kwargs)
        elif cls.default_strategy == STUB_STRATEGY:
            return cls.stub(**kwargs)
        else:
            raise BaseFactory.UnknownStrategy('Unknown default_strategy: {0}'.format(cls.default_strategy))

    def __new__(cls, class_name, bases, attrs, extra_attrs=None):
        """Record attributes as a pattern for later instance construction.

        This is called when a new Factory subclass is defined; it will collect
        attribute declaration from the class definition.

        Args:
            class_name (str): the name of the class being created
            bases (list of class): the parents of the class being created
            attrs (str => obj dict): the attributes as defined in the class
                definition
            extra_attrs (str => obj dict): extra attributes that should not be
                included in the factory defaults, even if public. This
                argument is only provided by extensions of this metaclass.

        Returns:
            A new class
        """

        parent_factories = get_factory_bases(bases)
        if not parent_factories or attrs.get('ABSTRACT_FACTORY', False):
            # If this isn't a subclass of Factory, or specifically declared
            # abstract, don't do anything special.
            return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, attrs)

        declarations = containers.DeclarationDict()

        # Add parent declarations in reverse order.
        for base in reversed(parent_factories):
            # Import all 'public' attributes (avoid those starting with _)
            declarations.update_with_public(getattr(base, CLASS_ATTRIBUTE_DECLARATIONS, {}))

        # Import attributes from the class definition, storing protected/private
        # attributes in 'non_factory_attrs'.
        non_factory_attrs = declarations.update_with_public(attrs)

        # Store the DeclarationDict in the attributes of the newly created class
        non_factory_attrs[CLASS_ATTRIBUTE_DECLARATIONS] = declarations

        # Add extra args if provided.
        if extra_attrs:
            non_factory_attrs.update(extra_attrs)

        return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, non_factory_attrs)


class FactoryMetaClass(BaseFactoryMetaClass):
    """Factory metaclass for handling class association and ordered declarations."""

    ERROR_MESSAGE = """Could not determine what class this factory is for.
    Use the {0} attribute to specify a class."""
    ERROR_MESSAGE_AUTODISCOVERY = ERROR_MESSAGE + """
    Also, autodiscovery failed using the name '{1}'
    based on the Factory name '{2}' in {3}."""

    @classmethod
    def _discover_associated_class(cls, class_name, attrs, inherited=None):
        """Try to find the class associated with this factory.

        In order, the following tests will be performed:
        - Lookup the FACTORY_CLASS_DECLARATION attribute
        - If the newly created class is named 'FooBarFactory', look for a FooBar
            class in its module
        - If an inherited associated class was provided, use it.

        Args:
            class_name (str): the name of the factory class being created
            attrs (dict): the dict of attributes from the factory class
                definition
            inherited (class): the optional associated class inherited from a
                parent factory

        Returns:
            class: the class to associate with this factory

        Raises:
            AssociatedClassError: If we were unable to associate this factory
                to a class.
        """
        own_associated_class = None
        used_auto_discovery = False

        if FACTORY_CLASS_DECLARATION in attrs:
            return attrs[FACTORY_CLASS_DECLARATION]

        if '__module__' in attrs:
            factory_module = sys.modules[attrs['__module__']]
            if class_name.endswith('Factory'):
                # Try a module lookup
                used_auto_discovery = True
                associated_class_name = class_name[:-len('Factory')]
                if associated_class_name:
                    # Class name was longer than just 'Factory'.
                    try:
                        return getattr(factory_module, associated_class_name)
                    except AttributeError:
                        pass

        # Unable to guess a good option; return the inherited class.
        if inherited is not None:
            return inherited

        # Unable to find an associated class; fail.
        if used_auto_discovery:
            raise Factory.AssociatedClassError(
                FactoryMetaClass.ERROR_MESSAGE_AUTODISCOVERY.format(
                    FACTORY_CLASS_DECLARATION,
                    associated_class_name,
                    class_name,
                    factory_module,))
        else:
            raise Factory.AssociatedClassError(
                FactoryMetaClass.ERROR_MESSAGE.format(
                    FACTORY_CLASS_DECLARATION))

    def __new__(cls, class_name, bases, attrs):
        """Determine the associated class based on the factory class name. Record the associated class
        for construction of an associated class instance at a later time."""

        parent_factories = get_factory_bases(bases)
        if not parent_factories or attrs.get('ABSTRACT_FACTORY', False):
            # If this isn't a subclass of Factory, don't do anything special.
            return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, attrs)

        base = parent_factories[0]

        inherited_associated_class = getattr(base,
                CLASS_ATTRIBUTE_ASSOCIATED_CLASS, None)
        associated_class = cls._discover_associated_class(class_name, attrs,
                inherited_associated_class)

        # Remove the FACTORY_CLASS_DECLARATION attribute from attrs, if present.
        attrs.pop(FACTORY_CLASS_DECLARATION, None)

        # If inheriting the factory from a parent, keep a link to it.
        # This allows to use the sequence counters from the parents.
        if associated_class == inherited_associated_class:
            attrs['_base_factory'] = base

        # The CLASS_ATTRIBUTE_ASSOCIATED_CLASS must *not* be taken into account
        # when parsing the declared attributes of the new class.
        extra_attrs = {CLASS_ATTRIBUTE_ASSOCIATED_CLASS: associated_class}

        return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, attrs, extra_attrs=extra_attrs)


# Factory base classes

class BaseFactory(object):
    """Factory base support for sequences, attributes and stubs."""

    class UnknownStrategy(RuntimeError):
        pass

    class UnsupportedStrategy(RuntimeError):
        pass

    def __new__(cls, *args, **kwargs):
        """Would be called if trying to instantiate the class."""
        raise RuntimeError('You cannot instantiate BaseFactory')

    # ID to use for the next 'declarations.Sequence' attribute.
    _next_sequence = None

    # Base factory, if this class was inherited from another factory. This is
    # used for sharing the _next_sequence counter among factories for the same
    # class.
    _base_factory = None

    @classmethod
    def _setup_next_sequence(cls):
        """Set up an initial sequence value for Sequence attributes.

        Returns:
            int: the first available ID to use for instances of this factory.
        """
        return 0

    @classmethod
    def _generate_next_sequence(cls):
        """Retrieve a new sequence ID.

        This will call, in order:
        - _generate_next_sequence from the base factory, if provided
        - _setup_next_sequence, if this is the 'toplevel' factory and the
            sequence counter wasn't initialized yet; then increase it.
        """

        # Rely upon our parents
        if cls._base_factory:
            return cls._base_factory._generate_next_sequence()

        # Make sure _next_sequence is initialized
        if cls._next_sequence is None:
            cls._next_sequence = cls._setup_next_sequence()

        # Pick current value, then increase class counter for the next call.
        next_sequence = cls._next_sequence
        cls._next_sequence += 1
        return next_sequence

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
        return containers.AttributeBuilder(cls, extra).build(create)

    @classmethod
    def declarations(cls, extra_defs=None):
        """Retrieve a copy of the declared attributes.

        Args:
            extra_defs (dict): additional definitions to insert into the
                retrieved DeclarationDict.
        """
        return getattr(cls, CLASS_ATTRIBUTE_DECLARATIONS).copy(extra_defs)

    @classmethod
    def build(cls, **kwargs):
        """Build an instance of the associated class, with overriden attrs."""
        raise cls.UnsupportedStrategy()

    @classmethod
    def create(cls, **kwargs):
        """Create an instance of the associated class, with overriden attrs."""
        raise cls.UnsupportedStrategy()

    @classmethod
    def stub(cls, **kwargs):
        """Retrieve a stub of the associated class, with overriden attrs.

        This will return an object whose attributes are those defined in this
        factory's declarations or in the extra kwargs.
        """
        stub_object = containers.StubObject()
        for name, value in cls.attributes(create=False, extra=kwargs).iteritems():
            setattr(stub_object, name, value)
        return stub_object


class StubFactory(BaseFactory):
    __metaclass__ = BaseFactoryMetaClass

    default_strategy = STUB_STRATEGY


class Factory(BaseFactory):
    """Factory base with build and create support.

    This class has the ability to support multiple ORMs by using custom creation
    functions.
    """
    __metaclass__ = FactoryMetaClass

    default_strategy = CREATE_STRATEGY

    class AssociatedClassError(RuntimeError):
        pass

    # Customizing 'create' strategy, using a tuple to keep the creation function
    # from turning it into an instance method.
    _creation_function = (DJANGO_CREATION,)

    @classmethod
    def set_creation_function(cls, creation_function):
        """Set the creation function for this class.

        Args:
            creation_function (function): the new creation function. That
                function should take one non-keyword argument, the 'class' for
                which an instance will be created. The value of the various
                fields are passed as keyword arguments.
        """
        cls._creation_function = (creation_function,)

    @classmethod
    def get_creation_function(cls):
        """Retrieve the creation function for this class.

        Returns:
            function: A function that takes one parameter, the class for which
                an instance will be created, and keyword arguments for the value
                of the fields of the instance.
        """
        return cls._creation_function[0]

    # Customizing 'build' strategy, using a tuple to keep the creation function
    # from turning it into an instance method.
    _building_function = (NAIVE_BUILD,)

    @classmethod
    def set_building_function(cls, building_function):
        """Set the building function for this class.

        Args:
            building_function (function): the new building function. That
                function should take one non-keyword argument, the 'class' for
                which an instance will be built. The value of the various
                fields are passed as keyword arguments.
        """
        cls._building_function = (building_function,)

    @classmethod
    def get_building_function(cls):
        """Retrieve the building function for this class.

        Returns:
            function: A function that takes one parameter, the class for which
                an instance will be created, and keyword arguments for the value
                of the fields of the instance.
        """
        return cls._building_function[0]

    @classmethod
    def _prepare(cls, create, **kwargs):
        """Prepare an object for this factory.

        Args:
            create: bool, whether to create or to build the object
            **kwargs: arguments to pass to the creation function
        """
        if create:
            return cls.get_creation_function()(getattr(cls, CLASS_ATTRIBUTE_ASSOCIATED_CLASS), **kwargs)
        else:
            return cls.get_building_function()(getattr(cls, CLASS_ATTRIBUTE_ASSOCIATED_CLASS), **kwargs)

    @classmethod
    def _build(cls, **kwargs):
        return cls._prepare(create=False, **kwargs)

    @classmethod
    def _create(cls, **kwargs):
        return cls._prepare(create=True, **kwargs)

    @classmethod
    def build(cls, **kwargs):
        return cls._build(**cls.attributes(create=False, extra=kwargs))

    @classmethod
    def create(cls, **kwargs):
        return cls._create(**cls.attributes(create=True, extra=kwargs))


class DjangoModelFactory(Factory):
    """Factory for Django models.

    This makes sure that the 'sequence' field of created objects is an unused id.

    Possible improvement: define a new 'attribute' type, AutoField, which would
    handle those for non-numerical primary keys.
    """

    ABSTRACT_FACTORY = True

    @classmethod
    def _setup_next_sequence(cls):
        """Compute the next available ID, based on the 'id' database field."""
        try:
            return 1 + cls._associated_class._default_manager.values_list('id', flat=True
                ).order_by('-id')[0]
        except IndexError:
            return 1


def make_factory(klass, **kwargs):
    """Create a new, simple factory for the given class."""
    factory_name = '%sFactory' % klass.__name__
    kwargs[FACTORY_CLASS_DECLARATION] = klass
    factory_class = type(Factory).__new__(type(Factory), factory_name, (Factory,), kwargs)
    factory_class.__name__ = '%sFactory' % klass.__name__
    factory_class.__doc__ = 'Auto-generated factory for class %s' % klass
    return factory_class


def build(klass, **kwargs):
    """Create a factory for the given class, and build an instance."""
    return make_factory(klass, **kwargs).build()

def create(klass, **kwargs):
    """Create a factory for the given class, and create an instance."""
    return make_factory(klass, **kwargs).create()

def stub(klass, **kwargs):
    """Create a factory for the given class, and stub an instance."""
    return make_factory(klass, **kwargs).stub()
