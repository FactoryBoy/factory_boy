# Copyright (c) 2010 Mark Sandstrom
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

from containers import AttributeBuilder, DeclarationDict, StubObject
from declarations import OrderedDeclaration

# Strategies

BUILD_STRATEGY = 'build'
CREATE_STRATEGY = 'create'
STUB_STRATEGY = 'stub'

# Creation functions. Use Factory.set_creation_function() to set a creation function appropriate for your ORM.

DJANGO_CREATION = lambda class_to_create, **kwargs: class_to_create.objects.create(**kwargs)

# Special declarations

FACTORY_CLASS_DECLARATION = 'FACTORY_FOR'

# Factory class attributes

CLASS_ATTRIBUTE_DECLARATIONS = '_declarations'
CLASS_ATTRIBUTE_ASSOCIATED_CLASS = '_associated_class'

# Factory metaclasses

def get_factory_base(bases):
    return [b for b in bases if isinstance(b, BaseFactoryMetaClass)]


class BaseFactoryMetaClass(type):
    """Factory metaclass for handling ordered declarations."""

    def __call__(cls, **kwargs):
        """Create an associated class instance using the default build strategy. Never create a Factory instance."""

        if cls.default_strategy == BUILD_STRATEGY:
            return cls.build(**kwargs)
        elif cls.default_strategy == CREATE_STRATEGY:
            return cls.create(**kwargs)
        elif cls.default_strategy == STUB_STRATEGY:
            return cls.stub(**kwargs)
        else:
            raise BaseFactory.UnknownStrategy('Unknown default_strategy: {0}'.format(cls.default_strategy))

    def __new__(cls, class_name, bases, attrs, extra_attrs={}):
        """Record attributes (unordered declarations) and ordered declarations for construction of
        an associated class instance at a later time."""

        parent_factories = get_factory_base(bases)
        if not parent_factories or attrs.get('ABSTRACT_FACTORY', False):
            # If this isn't a subclass of Factory, don't do anything special.
            return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, attrs)

        declarations = DeclarationDict()

        #Add parent declarations in reverse order.
        for base in reversed(parent_factories):
            declarations.update_with_public(getattr(base, CLASS_ATTRIBUTE_DECLARATIONS, {}))

        non_factory_attrs = declarations.update_with_public(attrs)
        non_factory_attrs[CLASS_ATTRIBUTE_DECLARATIONS] = declarations
        non_factory_attrs.update(extra_attrs)

        return super(BaseFactoryMetaClass, cls).__new__(cls, class_name, bases, non_factory_attrs)


class FactoryMetaClass(BaseFactoryMetaClass):
    """Factory metaclass for handling class association and ordered declarations."""

    ERROR_MESSAGE = """Could not determine what class this factory is for.
    Use the {0} attribute to specify a class."""
    ERROR_MESSAGE_AUTODISCOVERY = ERROR_MESSAGE + """
    Also, autodiscovery failed using the name '{1}'
    based on the Factory name '{2}' in {3}."""

    def __new__(cls, class_name, bases, attrs):
        """Determine the associated class based on the factory class name. Record the associated class
        for construction of an associated class instance at a later time."""

        parent_factories = get_factory_base(bases)
        if not parent_factories or attrs.get('ABSTRACT_FACTORY', False):
            # If this isn't a subclass of Factory, don't do anything special.
            return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, attrs)

        base = parent_factories[0]

        inherited_associated_class = getattr(base, CLASS_ATTRIBUTE_ASSOCIATED_CLASS, None)
        own_associated_class = None
        used_auto_discovery = False

        if FACTORY_CLASS_DECLARATION in attrs:
            own_associated_class = attrs.pop(FACTORY_CLASS_DECLARATION)
        else:
            factory_module = sys.modules[attrs['__module__']]
            match = re.match(r'^(\w+)Factory$', class_name)
            if match:
                used_auto_discovery = True
                associated_class_name = match.group(1)
                try:
                    own_associated_class = getattr(factory_module, associated_class_name)
                except AttributeError:
                    pass

        if own_associated_class is None and inherited_associated_class is not None:
            own_associated_class = inherited_associated_class
            attrs['_base_factory'] = base

        if not own_associated_class:
            if used_auto_discovery:
                format_args = FACTORY_CLASS_DECLARATION, associated_class_name, class_name, factory_module
                raise Factory.AssociatedClassError(FactoryMetaClass.ERROR_MESSAGE_AUTODISCOVERY.format(*format_args))
            else:
                raise Factory.AssociatedClassError(FactoryMetaClass.ERROR_MESSAGE.format(FACTORY_CLASS_DECLARATION))

        extra_attrs = {CLASS_ATTRIBUTE_ASSOCIATED_CLASS: own_associated_class}
        return super(FactoryMetaClass, cls).__new__(cls, class_name, bases, attrs, extra_attrs=extra_attrs)

# Factory base classes

class BaseFactory(object):
    """Factory base support for sequences, attributes and stubs."""

    class UnknownStrategy(RuntimeError): pass
    class UnsupportedStrategy(RuntimeError): pass

    def __new__(cls, *args, **kwargs):
        raise RuntimeError('You cannot instantiate BaseFactory')

    _next_sequence = None
    _base_factory = None

    @classmethod
    def _setup_next_sequence(cls):
        """Set up an initial sequence value for Sequence attributes."""
        return 0

    @classmethod
    def _generate_next_sequence(cls):
        if cls._base_factory:
            return cls._base_factory._generate_next_sequence()
        if cls._next_sequence is None:
            cls._next_sequence = cls._setup_next_sequence()
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
        return AttributeBuilder(cls, extra).build(create)

    @classmethod
    def declarations(cls, extra_defs=None):
        return getattr(cls, CLASS_ATTRIBUTE_DECLARATIONS).copy(extra_defs)

    @classmethod
    def build(cls, **kwargs):
        raise cls.UnsupportedStrategy()

    @classmethod
    def create(cls, **kwargs):
        raise cls.UnsupportedStrategy()

    @classmethod
    def stub(cls, **kwargs):
        stub_object = StubObject()
        for name, value in cls.attributes(create=False, extra=kwargs).iteritems():
            setattr(stub_object, name, value)
        return stub_object


class StubFactory(BaseFactory):
    __metaclass__ = BaseFactoryMetaClass

    default_strategy = STUB_STRATEGY


class Factory(BaseFactory):
    """Factory base with build and create support.

    This class has the ability to support multiple ORMs by using custom creation functions."""

    __metaclass__ = FactoryMetaClass

    default_strategy = CREATE_STRATEGY

    class AssociatedClassError(RuntimeError): pass

    _creation_function = (DJANGO_CREATION,)  # Using a tuple to keep the creation function from turning into an instance method
    @classmethod
    def set_creation_function(cls, creation_function):
        cls._creation_function = (creation_function,)
    @classmethod
    def get_creation_function(cls):
        return cls._creation_function[0]

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
            return getattr(cls, CLASS_ATTRIBUTE_ASSOCIATED_CLASS)(**kwargs)

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
    """Factory for django models.

    This makes sure that the 'sequence' field of created objects is an unused id.

    Possible improvement: define a new 'attribute' type, AutoField, which would
    handle those for non-numerical primary keys.
    """

    ABSTRACT_FACTORY = True

    @classmethod
    def _setup_next_sequence(cls):
        try:
            return cls._associated_class.objects.values_list('id', flat=True).order_by('-id')[0] + 1
        except IndexError:
            return 1
