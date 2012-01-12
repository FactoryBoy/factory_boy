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


class SelfAttribute(OrderedDeclaration):
    """Specific OrderedDeclaration copying values from other fields.

    Attributes:
        attribute_name (str): the name of the attribute to copy.
    """

    def __init__(self, attribute_name, *args, **kwargs):
        super(SelfAttribute, self).__init__(*args, **kwargs)
        self.attribute_name = attribute_name

    def evaluate(self, sequence, obj, containers=()):
        # TODO(rbarrois): allow the use of ATTR_SPLITTER to fetch fields of
        # subfactories.
        return getattr(obj, self.attribute_name)


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


class LazyContainerAttribute(OrderedDeclaration):
    """Variant of LazyAttribute, also receives the containers of the object.

    Attributes:
        function (function): A function, expecting the current LazyStub and the
            (optional) object having a subfactory containing this attribute.
        strict (bool): Whether evaluating should fail when the containers are
            not passed in (i.e used outside a SubFactory).
    """
    def __init__(self, function, strict=True, *args, **kwargs):
        super(LazyContainerAttribute, self).__init__(*args, **kwargs)
        self.function = function
        self.strict = strict

    def evaluate(self, sequence, obj, containers=()):
        """Evaluate the current LazyContainerAttribute.

        Args:
            obj (LazyStub): a lazy stub of the object being constructed, if
                needed.
            containers (LazyStub): a lazy stub of a factory being evaluated, with
                a SubFactory building 'obj'.
        """
        if self.strict and not containers:
            raise TypeError(
                "A LazyContainerAttribute in 'strict' mode can only be used "
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
        """

        defaults = dict(self.defaults)
        if extra:
            defaults.update(extra)
        defaults['__containers'] = containers

        attrs = self.factory.attributes(create, defaults)

        if create:
            return self.factory.create(**attrs)
        else:
            return self.factory.build(**attrs)


# Decorators... in case lambdas don't cut it

def lazy_attribute(func):
    return LazyAttribute(func)

def sequence(func):
    return Sequence(func)

def lazy_attribute_sequence(func):
    return LazyAttributeSequence(func)

def lazy_container_attribute(func):
    return LazyContainerAttribute(func, strict=False)
