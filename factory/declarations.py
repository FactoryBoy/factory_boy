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


import itertools

from factory import utils


class OrderedDeclaration(object):
    """A factory declaration.

    Ordered declarations mark an attribute as needing lazy evaluation.
    This allows them to refer to attributes defined by other OrderedDeclarations
    in the same factory.
    """

    def evaluate(self, sequence, obj, containers=()):
        """Evaluate this declaration.

        Args:
            sequence (int): the current sequence counter to use when filling
                the current instance
            obj (containers.LazyStub): The object holding currently computed
                attributes
            containers (list of containers.LazyStub): The chain of SubFactory
                which led to building this object.
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

    def evaluate(self, sequence, obj, containers=()):
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

    Attributes:
        attribute_name (str): the name of the attribute to copy.
        default (object): the default value to use if the attribute doesn't
            exist.
    """

    def __init__(self, attribute_name, default=_UNSPECIFIED, *args, **kwargs):
        super(SelfAttribute, self).__init__(*args, **kwargs)
        self.attribute_name = attribute_name
        self.default = default

    def evaluate(self, sequence, obj, containers=()):
        return deepgetattr(obj, self.attribute_name, self.default)


class Iterator(OrderedDeclaration):
    """Fill this value using the values returned by an iterator.

    Warning: the iterator should not end !

    Attributes:
        iterator (iterable): the iterator whose value should be used.
    """

    def __init__(self, iterator):
        super(Iterator, self).__init__()
        self.iterator = iter(iterator)

    def evaluate(self, sequence, obj, containers=()):
        return self.iterator.next()


class InfiniteIterator(Iterator):
    """Same as Iterator, but make the iterator infinite by cycling at the end.

    Attributes:
        iterator (iterable): the iterator, once made infinite.
    """

    def __init__(self, iterator):
        return super(InfiniteIterator, self).__init__(itertools.cycle(iterator))


class Sequence(OrderedDeclaration):
    """Specific OrderedDeclaration to use for 'sequenced' fields.

    These fields are typically used to generate increasing unique values.

    Attributes:
        function (function): A function, expecting the current sequence counter
            and returning the computed value.
        type (function): A function converting an integer into the expected kind
            of counter for the 'function' attribute.
    """
    def __init__(self, function, type=str):
        super(Sequence, self).__init__()
        self.function = function
        self.type = type

    def evaluate(self, sequence, obj, containers=()):
        return self.function(self.type(sequence))


class LazyAttributeSequence(Sequence):
    """Composite of a LazyAttribute and a Sequence.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            current sequence counter.
        type (function): A function converting an integer into the expected kind
            of counter for the 'function' attribute.
    """
    def evaluate(self, sequence, obj, containers=()):
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

    def evaluate(self, sequence, obj, containers=()):
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


class SubFactory(OrderedDeclaration):
    """Base class for attributes based upon a sub-factory.

    Attributes:
        defaults (dict): Overrides to the defaults defined in the wrapped
            factory
        factory (base.Factory): the wrapped factory
    """

    def __init__(self, factory, **kwargs):
        super(SubFactory, self).__init__()
        self.defaults = kwargs
        self.factory = factory

    def evaluate(self, create, extra, containers):
        """Evaluate the current definition and fill its attributes.

        Uses attributes definition in the following order:
        - attributes defined in the wrapped factory class
        - values defined when defining the SubFactory
        - additional values defined in attributes

        Args:
            create (bool): whether the subfactory should call 'build' or
                'create'
            extra (containers.DeclarationDict): extra values that should
                override the wrapped factory's defaults
            containers (list of LazyStub): List of LazyStub for the chain of
                factories being evaluated, the calling stub being first.
        """

        defaults = dict(self.defaults)
        if extra:
            defaults.update(extra)
        defaults['__containers'] = containers

        if create:
            return self.factory.create(**defaults)
        else:
            return self.factory.build(**defaults)


class PostGenerationDeclaration(object):
    """Declarations to be called once the target object has been generated.

    Attributes:
        extract_prefix (str): prefix to use when extracting attributes from
            the factory's declaration for this declaration. If empty, uses
            the attribute name of the PostGenerationDeclaration.
    """

    def __init__(self, extract_prefix=None):
        self.extract_prefix = extract_prefix

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
        if self.extract_prefix:
            extract_prefix = self.extract_prefix
        else:
            extract_prefix = name
        extracted = attrs.pop(extract_prefix, None)
        kwargs = utils.extract_dict(extract_prefix, attrs)
        return extracted, kwargs

    def call(self, obj, create, extracted=None, **kwargs):
        """Call this hook; no return value is expected.

        Args:
            obj (object): the newly generated object
            create (bool): whether the object was 'built' or 'created'
            extracted (object): the value given for <extract_prefix> in the
                object definition, or None if not provided.
            kwargs (dict): declarations extracted from the object
                definition for this hook
        """
        raise NotImplementedError()


class PostGeneration(PostGenerationDeclaration):
    """Calls a given function once the object has been generated."""
    def __init__(self, function, extract_prefix=None):
        super(PostGeneration, self).__init__(extract_prefix)
        self.function = function

    def call(self, obj, create, extracted=None, **kwargs):
        self.function(obj, create, extracted, **kwargs)


def post_generation(extract_prefix=None):
    def decorator(fun):
        return PostGeneration(fun, extract_prefix=extract_prefix)
    return decorator


class RelatedFactory(PostGenerationDeclaration):
    """Calls a factory once the object has been generated.

    Attributes:
        factory (Factory): the factory to call
        defaults (dict): extra declarations for calling the related factory
        name (str): the name to use to refer to the generated object when
            calling the related factory
    """

    def __init__(self, factory, name='', **defaults):
        super(RelatedFactory, self).__init__(extract_prefix=None)
        self.factory = factory
        self.name = name
        self.defaults = defaults

    def call(self, obj, create, extracted=None, **kwargs):
        passed_kwargs = dict(self.defaults)
        passed_kwargs.update(kwargs)
        if self.name:
            passed_kwargs[self.name] = obj
        self.factory.simple_generate(create, **passed_kwargs)


class PostGenerationMethodCall(PostGenerationDeclaration):
    """Calls a method of the generated object.

    Attributes:
        method_name (str): the method to call
        method_args (list): arguments to pass to the method
        method_kwargs (dict): keyword arguments to pass to the method

    Example:
        class UserFactory(factory.Factory):
            ...
            password = factory.PostGenerationMethodCall('set_password', password='')
    """
    def __init__(self, method_name, extract_prefix=None, *args, **kwargs):
        super(PostGenerationMethodCall, self).__init__(extract_prefix)
        self.method_name = method_name
        self.method_args = args
        self.method_kwargs = kwargs

    def call(self, obj, create, extracted=None, **kwargs):
        passed_kwargs = dict(self.method_kwargs)
        passed_kwargs.update(kwargs)
        method = getattr(obj, self.method_name)
        method(*self.method_args, **passed_kwargs)


# Decorators... in case lambdas don't cut it

def lazy_attribute(func):
    return LazyAttribute(func)

def iterator(func):
    """Turn a generator function into an iterator attribute."""
    return Iterator(func())

def infinite_iterator(func):
    """Turn a generator function into an infinite iterator attribute."""
    return InfiniteIterator(func())

def sequence(func):
    return Sequence(func)

def lazy_attribute_sequence(func):
    return LazyAttributeSequence(func)

def container_attribute(func):
    return ContainerAttribute(func, strict=False)
