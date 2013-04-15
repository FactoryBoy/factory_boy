# -*- coding: utf-8 -*-
# Copyright (c) 2010 Mark Sandstrom
# Copyright (c) 2011-2013 Raphaël Barrois
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


import itertools

from . import compat
from . import utils


class OrderedDeclaration(object):
    """A factory declaration.

    Ordered declarations mark an attribute as needing lazy evaluation.
    This allows them to refer to attributes defined by other OrderedDeclarations
    in the same factory.
    """

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        """Evaluate this declaration.

        Args:
            sequence (int): the current sequence counter to use when filling
                the current instance
            obj (containers.LazyStub): The object holding currently computed
                attributes
            containers (list of containers.LazyStub): The chain of SubFactory
                which led to building this object.
            create (bool): whether the target class should be 'built' or
                'created'
            extra (DeclarationDict or None): extracted key/value extracted from
                the attribute prefix
        """
        raise NotImplementedError('This is an abstract method')


class LazyAttribute(OrderedDeclaration):
    """Specific OrderedDeclaration computed using a lambda.

    Attributes:
        function (function): a function, expecting the current LazyStub and
            returning the computed value.
    """

    def __init__(self, function, *args, **kwargs):
        super(LazyAttribute, self).__init__(*args, **kwargs)
        self.function = function

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        return self.function(obj)


class _UNSPECIFIED(object):
    pass


def deepgetattr(obj, name, default=_UNSPECIFIED):
    """Try to retrieve the given attribute of an object, digging on '.'.

    This is an extended getattr, digging deeper if '.' is found.

    Args:
        obj (object): the object of which an attribute should be read
        name (str): the name of an attribute to look up.
        default (object): the default value to use if the attribute wasn't found

    Returns:
        the attribute pointed to by 'name', splitting on '.'.

    Raises:
        AttributeError: if obj has no 'name' attribute.
    """
    try:
        if '.' in name:
            attr, subname = name.split('.', 1)
            return deepgetattr(getattr(obj, attr), subname, default)
        else:
            return getattr(obj, name)
    except AttributeError:
        if default is _UNSPECIFIED:
            raise
        else:
            return default


class SelfAttribute(OrderedDeclaration):
    """Specific OrderedDeclaration copying values from other fields.

    If the field name starts with two dots or more, the lookup will be anchored
    in the related 'parent'.

    Attributes:
        depth (int): the number of steps to go up in the containers chain
        attribute_name (str): the name of the attribute to copy.
        default (object): the default value to use if the attribute doesn't
            exist.
    """

    def __init__(self, attribute_name, default=_UNSPECIFIED, *args, **kwargs):
        super(SelfAttribute, self).__init__(*args, **kwargs)
        depth = len(attribute_name) -  len(attribute_name.lstrip('.'))
        attribute_name = attribute_name[depth:]

        self.depth = depth
        self.attribute_name = attribute_name
        self.default = default

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        if self.depth > 1:
            # Fetching from a parent
            target = containers[self.depth - 2]
        else:
            target = obj
        return deepgetattr(target, self.attribute_name, self.default)

    def __repr__(self):
        return '<%s(%r, default=%r)>' % (
            self.__class__.__name__,
            self.attribute_name,
            self.default,
        )


class Iterator(OrderedDeclaration):
    """Fill this value using the values returned by an iterator.

    Warning: the iterator should not end !

    Attributes:
        iterator (iterable): the iterator whose value should be used.
        getter (callable or None): a function to parse returned values
    """

    def __init__(self, iterator, cycle=True, getter=None):
        super(Iterator, self).__init__()
        self.getter = getter

        if cycle:
            self.iterator = itertools.cycle(iterator)
        else:
            self.iterator = iter(iterator)

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        value = next(self.iterator)
        if self.getter is None:
            return value
        return self.getter(value)


class Sequence(OrderedDeclaration):
    """Specific OrderedDeclaration to use for 'sequenced' fields.

    These fields are typically used to generate increasing unique values.

    Attributes:
        function (function): A function, expecting the current sequence counter
            and returning the computed value.
        type (function): A function converting an integer into the expected kind
            of counter for the 'function' attribute.
    """
    def __init__(self, function, type=int):  # pylint: disable=W0622
        super(Sequence, self).__init__()
        self.function = function
        self.type = type

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        return self.function(self.type(sequence))


class LazyAttributeSequence(Sequence):
    """Composite of a LazyAttribute and a Sequence.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            current sequence counter.
        type (function): A function converting an integer into the expected kind
            of counter for the 'function' attribute.
    """
    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        return self.function(obj, self.type(sequence))


class ContainerAttribute(OrderedDeclaration):
    """Variant of LazyAttribute, also receives the containers of the object.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            (optional) object having a subfactory containing this attribute.
        strict (bool): Whether evaluating should fail when the containers are
            not passed in (i.e used outside a SubFactory).
    """
    def __init__(self, function, strict=True, *args, **kwargs):
        super(ContainerAttribute, self).__init__(*args, **kwargs)
        self.function = function
        self.strict = strict

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        """Evaluate the current ContainerAttribute.

        Args:
            obj (LazyStub): a lazy stub of the object being constructed, if
                needed.
            containers (list of LazyStub): a list of lazy stubs of factories
                being evaluated in a chain, each item being a future field of
                next one.
        """
        if self.strict and not containers:
            raise TypeError(
                "A ContainerAttribute in 'strict' mode can only be used "
                "within a SubFactory.")

        return self.function(obj, containers)


class ParameteredAttribute(OrderedDeclaration):
    """Base class for attributes expecting parameters.

    Attributes:
        defaults (dict): Default values for the paramters.
            May be overridden by call-time parameters.

    Class attributes:
        CONTAINERS_FIELD (str): name of the field, if any, where container
            information (e.g for SubFactory) should be stored. If empty,
            containers data isn't merged into generate() parameters.
    """

    CONTAINERS_FIELD = '__containers'

    # Whether to add the current object to the stack of containers
    EXTEND_CONTAINERS = False

    def __init__(self, **kwargs):
        super(ParameteredAttribute, self).__init__()
        self.defaults = kwargs

    def _prepare_containers(self, obj, containers=()):
        if self.EXTEND_CONTAINERS:
            return (obj,) + tuple(containers)

        return containers

    def evaluate(self, sequence, obj, create, extra=None, containers=()):
        """Evaluate the current definition and fill its attributes.

        Uses attributes definition in the following order:
        - values defined when defining the ParameteredAttribute
        - additional values defined when instantiating the containing factory

        Args:
            create (bool): whether the parent factory is being 'built' or
                'created'
            extra (containers.DeclarationDict): extra values that should
                override the defaults
            containers (list of LazyStub): List of LazyStub for the chain of
                factories being evaluated, the calling stub being first.
        """
        defaults = dict(self.defaults)
        if extra:
            defaults.update(extra)
        if self.CONTAINERS_FIELD:
            containers = self._prepare_containers(obj, containers)
            defaults[self.CONTAINERS_FIELD] = containers

        return self.generate(sequence, obj, create, defaults)

    def generate(self, sequence, obj, create, params):  # pragma: no cover
        """Actually generate the related attribute.

        Args:
            sequence (int): the current sequence number
            obj (LazyStub): the object being constructed
            create (bool): whether the calling factory was in 'create' or
                'build' mode
            params (dict): parameters inherited from init and evaluation-time
                overrides.

        Returns:
            Computed value for the current declaration.
        """
        raise NotImplementedError()


class SubFactory(ParameteredAttribute):
    """Base class for attributes based upon a sub-factory.

    Attributes:
        defaults (dict): Overrides to the defaults defined in the wrapped
            factory
        factory (base.Factory): the wrapped factory
    """

    EXTEND_CONTAINERS = True

    def __init__(self, factory, **kwargs):
        super(SubFactory, self).__init__(**kwargs)
        if isinstance(factory, type):
            self.factory = factory
            self.factory_module = self.factory_name = ''
        else:
            # Must be a string
            if not (compat.is_string(factory) and '.' in factory):
                raise ValueError(
                        "The argument of a SubFactory must be either a class "
                        "or the fully qualified path to a Factory class; got "
                        "%r instead." % factory)
            self.factory = None
            self.factory_module, self.factory_name = factory.rsplit('.', 1)

    def get_factory(self):
        """Retrieve the wrapped factory.Factory subclass."""
        if self.factory is None:
            # Must be a module path
            self.factory = utils.import_object(
                    self.factory_module, self.factory_name)
        return self.factory

    def generate(self, sequence, obj, create, params):
        """Evaluate the current definition and fill its attributes.

        Args:
            create (bool): whether the subfactory should call 'build' or
                'create'
            params (containers.DeclarationDict): extra values that should
                override the wrapped factory's defaults
        """
        subfactory = self.get_factory()
        return subfactory.simple_generate(create, **params)


class Dict(SubFactory):
    """Fill a dict with usual declarations."""

    def __init__(self, params, dict_factory='factory.DictFactory'):
        super(Dict, self).__init__(dict_factory, **dict(params))

    def generate(self, sequence, obj, create, params):
        dict_factory = self.get_factory()
        return dict_factory.simple_generate(create,
            __sequence=sequence,
            **params)


class List(SubFactory):
    """Fill a list with standard declarations."""

    def __init__(self, params, list_factory='factory.ListFactory'):
        params = dict((str(i), v) for i, v in enumerate(params))
        super(List, self).__init__(list_factory, **params)

    def generate(self, sequence, obj, create, params):
        list_factory = self.get_factory()
        return list_factory.simple_generate(create,
            __sequence=sequence,
            **params)


class PostGenerationDeclaration(object):
    """Declarations to be called once the target object has been generated."""

    def extract(self, name, attrs):
        """Extract relevant attributes from a dict.

        Args:
            name (str): the name at which this PostGenerationDeclaration was
                defined in the declarations
            attrs (dict): the attribute dict from which values should be
                extracted

        Returns:
            (object, dict): a tuple containing the attribute at 'name' (if
                provided) and a dict of extracted attributes
        """
        extracted = attrs.pop(name, None)
        kwargs = utils.extract_dict(name, attrs)
        return extracted, kwargs

    def call(self, obj, create, extracted=None, **kwargs):  # pragma: no cover
        """Call this hook; no return value is expected.

        Args:
            obj (object): the newly generated object
            create (bool): whether the object was 'built' or 'created'
            extracted (object): the value given for <name> in the
                object definition, or None if not provided.
            kwargs (dict): declarations extracted from the object
                definition for this hook
        """
        raise NotImplementedError()


class PostGeneration(PostGenerationDeclaration):
    """Calls a given function once the object has been generated."""
    def __init__(self, function):
        super(PostGeneration, self).__init__()
        self.function = function

    def call(self, obj, create, extracted=None, **kwargs):
        return self.function(obj, create, extracted, **kwargs)


class RelatedFactory(PostGenerationDeclaration):
    """Calls a factory once the object has been generated.

    Attributes:
        factory (Factory): the factory to call
        defaults (dict): extra declarations for calling the related factory
        name (str): the name to use to refer to the generated object when
            calling the related factory
    """

    def __init__(self, factory, name='', **defaults):
        super(RelatedFactory, self).__init__()
        self.name = name
        self.defaults = defaults

        if isinstance(factory, type):
            self.factory = factory
            self.factory_module = self.factory_name = ''
        else:
            # Must be a string
            if not (compat.is_string(factory) and '.' in factory):
                raise ValueError(
                        "The argument of a SubFactory must be either a class "
                        "or the fully qualified path to a Factory class; got "
                        "%r instead." % factory)
            self.factory = None
            self.factory_module, self.factory_name = factory.rsplit('.', 1)

    def get_factory(self):
        """Retrieve the wrapped factory.Factory subclass."""
        if self.factory is None:
            # Must be a module path
            self.factory = utils.import_object(
                    self.factory_module, self.factory_name)
        return self.factory

    def call(self, obj, create, extracted=None, **kwargs):
        passed_kwargs = dict(self.defaults)
        passed_kwargs.update(kwargs)
        if self.name:
            passed_kwargs[self.name] = obj

        factory = self.get_factory()
        factory.simple_generate(create, **passed_kwargs)


class PostGenerationMethodCall(PostGenerationDeclaration):
    """Calls a method of the generated object.

    Attributes:
        method_name (str): the method to call
        method_args (list): arguments to pass to the method
        method_kwargs (dict): keyword arguments to pass to the method

    Example:
        class UserFactory(factory.Factory):
            ...
            password = factory.PostGenerationMethodCall('set_pass', password='')
    """
    def __init__(self, method_name, *args, **kwargs):
        super(PostGenerationMethodCall, self).__init__()
        self.method_name = method_name
        self.method_args = args
        self.method_kwargs = kwargs

    def call(self, obj, create, extracted=None, **kwargs):
        if extracted is None:
            passed_args = self.method_args

        elif len(self.method_args) <= 1:
            # Max one argument expected
            passed_args = (extracted,)
        else:
            passed_args = tuple(extracted)

        passed_kwargs = dict(self.method_kwargs)
        passed_kwargs.update(kwargs)
        method = getattr(obj, self.method_name)
        method(*passed_args, **passed_kwargs)
