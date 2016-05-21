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

from __future__ import unicode_literals

import logging

from . import declarations
from . import errors
from . import utils

logger = logging.getLogger(__name__)


class LazyStub(object):
    """A generic container that only allows getting attributes.

    Attributes are set at instantiation time, values are computed lazily.

    Attributes:
        __initialized (bool): whether this object's __init__ as run. If set,
            setting any attribute will be prevented.
        __attrs (dict): maps attribute name to their declaration
        __values (dict): maps attribute name to computed value
        __pending (str list): names of the attributes whose value is being
            computed. This allows to detect cyclic lazy attribute definition.
        __containers (LazyStub list): "parents" of the LazyStub being built.
            This allows to have the field of a field depend on the value of
            another field
        __model_class (type): the model class to build.
    """

    __initialized = False

    def __init__(self, attrs, containers=(), model_class=object, log_ctx=None):
        self.__attrs = attrs
        self.__values = {}
        self.__pending = []
        self.__containers = containers
        self.__model_class = model_class
        self.__log_ctx = log_ctx or '%s.%s' % (model_class.__module__, model_class.__name__)
        self.factory_parent = containers[0] if containers else None
        self.__initialized = True

    def __repr__(self):
        return '<LazyStub for %s.%s>' % (self.__model_class.__module__, self.__model_class.__name__)

    def __str__(self):
        return '<LazyStub for %s with %s>' % (
            self.__model_class.__name__, list(self.__attrs.keys()))

    def __fill__(self):
        """Fill this LazyStub, computing values of all defined attributes.

        Retunrs:
            dict: map of attribute name => computed value
        """
        res = {}
        logger.debug(
            "LazyStub: Computing values for %s(%s)",
            self.__log_ctx, utils.log_pprint(kwargs=self.__attrs),
        )
        for attr in self.__attrs:
            res[attr] = getattr(self, attr)

        logger.debug(
            "LazyStub: Computed values, got %s(%s)",
            self.__log_ctx, utils.log_pprint(kwargs=res),
        )
        return res

    def __getattr__(self, name):
        """Retrieve an attribute's value.

        This will compute it if needed, unless it is already on the list of
        attributes being computed.
        """
        if name in self.__pending:
            raise errors.CyclicDefinitionError(
                "Cyclic lazy attribute definition for %s; cycle found in %r." %
                (name, self.__pending))
        elif name in self.__values:
            return self.__values[name]
        elif name in self.__attrs:
            val = self.__attrs[name]
            if isinstance(val, LazyValue):
                self.__pending.append(name)
                try:
                    val = val.evaluate(self, self.__containers)
                finally:
                    last = self.__pending.pop()
                assert name == last
            self.__values[name] = val
            return val
        else:
            raise AttributeError(
                "The parameter %s is unknown. Evaluated attributes are %r, "
                "definitions are %r." % (name, self.__values, self.__attrs))

    def __setattr__(self, name, value):
        """Prevent setting attributes once __init__ is done."""
        if not self.__initialized:
            return super(LazyStub, self).__setattr__(name, value)
        else:
            raise AttributeError('Setting of object attributes is not allowed')


class DeclarationStack(object):
    """An ordered stack of declarations.

    This is intended to handle declaration precedence among different mutating layers.
    """
    def __init__(self, ordering):
        self.ordering = ordering
        self.layers = dict((name, {}) for name in self.ordering)

    def __getitem__(self, key):
        return self.layers[key]

    def __setitem__(self, key, value):
        assert key in self.ordering
        self.layers[key] = value

    def current(self):
        """Retrieve the current, flattened declarations dict."""
        result = {}
        for layer in self.ordering:
            result.update(self.layers[layer])
        return result


class ParameterResolver(object):
    """Resolve a factory's parameter declarations."""
    def __init__(self, parameters, deps):
        self.parameters = parameters
        self.deps = deps
        self.declaration_stack = None

        self.resolved = set()

    def resolve_one(self, name):
        """Compute one field is needed, taking dependencies into accounts."""
        if name in self.resolved:
            return

        for dep in self.deps.get(name, ()):
            self.resolve_one(dep)

        self.compute(name)
        self.resolved.add(name)

    def compute(self, name):
        """Actually compute the value for a given name."""
        value = self.parameters[name]
        if isinstance(value, declarations.ComplexParameter):
            overrides = value.compute(name, self.declaration_stack.current())
        else:
            overrides = {name: value}
        self.declaration_stack['overrides'].update(overrides)

    def resolve(self, declaration_stack):
        """Resolve parameters for a given declaration stack.

        Modifies the stack in-place.
        """
        self.declaration_stack = declaration_stack
        for name in self.parameters:
            self.resolve_one(name)


class LazyValue(object):
    """Some kind of "lazy evaluating" object."""

    def evaluate(self, obj, containers=()):  # pragma: no cover
        """Compute the value, using the given object."""
        raise NotImplementedError("This is an abstract method.")


class DeclarationWrapper(LazyValue):
    """Lazy wrapper around an OrderedDeclaration.

    Attributes:
        declaration (declarations.OrderedDeclaration): the OrderedDeclaration
            being wrapped
        sequence (int): the sequence counter to use when evaluatin the
            declaration
    """

    def __init__(self, declaration, sequence, create, extra=None, **kwargs):
        super(DeclarationWrapper, self).__init__(**kwargs)
        self.declaration = declaration
        self.sequence = sequence
        self.create = create
        self.extra = extra

    def evaluate(self, obj, containers=()):
        """Lazily evaluate the attached OrderedDeclaration.

        Args:
            obj (LazyStub): the object being built
            containers (object list): the chain of containers of the object
                being built, its immediate holder being first.
        """
        return self.declaration.evaluate(
            self.sequence, obj,
            create=self.create,
            extra=self.extra,
            containers=containers,
        )

    def __repr__(self):
        return '<%s for %r>' % (self.__class__.__name__, self.declaration)


class AttributeBuilder(object):
    """Builds attributes from a factory and extra data.

    Attributes:
        factory (base.Factory): the Factory for which attributes are being
            built
        _declarations (DeclarationDict): the attribute declarations for the factory
        _subfields (dict): dict mapping an attribute name to a dict of
            overridden default values for the related SubFactory.
    """

    def __init__(self, factory, extra=None, log_ctx=None, **kwargs):
        super(AttributeBuilder, self).__init__(**kwargs)

        if not extra:
            extra = {}

        self.factory = factory
        self._containers = extra.pop('__containers', ())

        initial_declarations = dict(factory._meta.declarations)
        self._log_ctx = log_ctx

        # Parameters
        # ----------
        self._declarations = self.merge_declarations(initial_declarations, extra)

        # Subfields
        # ---------

        attrs_with_subfields = [
            k for k, v in initial_declarations.items()
            if self.has_subfields(v)
        ]

        # Extract subfields; THIS MODIFIES self._declarations.
        self._subfields = utils.multi_extract_dict(
            attrs_with_subfields, self._declarations)

    def has_subfields(self, value):
        return isinstance(value, declarations.ParameteredAttribute)

    def merge_declarations(self, initial, extra):
        """Compute the final declarations, taking into account paramter-based overrides."""
        # Precedence order:
        # - Start with class-level declarations
        # - Add overrides from parameters
        # - Finally, use callsite-level declarations & values
        declaration_stack = DeclarationStack(['initial', 'overrides', 'extra'])
        declaration_stack['initial'] = initial.copy()
        declaration_stack['extra'] = extra.copy()

        # Actually compute the final stack
        resolver = ParameterResolver(
            parameters=self.factory._meta.parameters,
            deps=self.factory._meta.parameters_dependencies,
        )
        resolver.resolve(declaration_stack)
        return declaration_stack.current()

    def build(self, create, force_sequence=None):
        """Build a dictionary of attributes.

        Args:
            create (bool): whether to 'build' or 'create' the subfactories.
            force_sequence (int or None): if set to an int, use this value for
                the sequence counter; don't advance the related counter.
        """
        # Setup factory sequence.
        if force_sequence is None:
            sequence = self.factory._generate_next_sequence()
        else:
            sequence = force_sequence

        # Parse attribute declarations, wrapping SubFactory and
        # OrderedDeclaration.
        wrapped_attrs = {}
        for k, v in self._declarations.items():
            if isinstance(v, declarations.OrderedDeclaration):
                v = DeclarationWrapper(
                    v,
                    sequence=sequence,
                    create=create,
                    extra=self._subfields.get(k, {}),
                )
            wrapped_attrs[k] = v

        stub = LazyStub(
            wrapped_attrs, containers=self._containers,
            model_class=self.factory, log_ctx=self._log_ctx)
        return stub.__fill__()


class StubObject(object):
    """A generic container."""
    pass
