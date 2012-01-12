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


from factory import declarations


#: String for splitting an attribute name into a
#: (subfactory_name, subfactory_field) tuple.
ATTR_SPLITTER = '__'


class CyclicDefinitionError(Exception):
    """Raised when cyclic definition were found."""


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
    """

    __initialized = False

    def __init__(self, attrs, containers=()):
        self.__attrs = attrs
        self.__values = {}
        self.__pending = []
        self.__containers = containers
        self.__initialized = True

    def __fill__(self):
        """Fill this LazyStub, computing values of all defined attributes.

        Retunrs:
            dict: map of attribute name => computed value
        """
        res = {}
        for attr in self.__attrs:
            res[attr] = getattr(self, attr)
        return res

    def __getattr__(self, name):
        """Retrieve an attribute's value.

        This will compute it if needed, unless it is already on the list of
        attributes being computed.
        """
        if name in self.__pending:
            raise CyclicDefinitionError(
                "Cyclic lazy attribute definition for %s; cycle found in %r." %
                (name, self.__pending))
        elif name in self.__values:
            return self.__values[name]
        elif name in self.__attrs:
            val = self.__attrs[name]
            if isinstance(val, LazyValue):
                self.__pending.append(name)
                val = val.evaluate(self, self.__containers)
                assert name == self.__pending.pop()
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


class DeclarationDict(dict):
    """Slightly extended dict to work with OrderedDeclaration."""

    def is_declaration(self, name, value):
        """Determines if a class attribute is a field value declaration.

        Based on the name and value of the class attribute, return ``True`` if
        it looks like a declaration of a default field value, ``False`` if it
        is private (name starts with '_') or a classmethod or staticmethod.

        """
        if isinstance(value, (classmethod, staticmethod)):
            return False
        elif isinstance(value, declarations.OrderedDeclaration):
            return True
        return (not name.startswith("_"))

    def update_with_public(self, d):
        """Updates the DeclarationDict from a class definition dict.

        Takes into account all public attributes and OrderedDeclaration
        instances; ignores all class/staticmethods and private attributes
        (starting with '_').

        Returns a dict containing all remaining elements.
        """
        remaining = {}
        for k, v in d.iteritems():
            if self.is_declaration(k, v):
                self[k] = v
            else:
                remaining[k] = v
        return remaining

    def copy(self, extra=None):
        """Copy this DeclarationDict into another one, including extra values.

        Args:
            extra (dict): additional attributes to include in the copy.
        """
        new = DeclarationDict()
        new.update(self)
        if extra:
            new.update(extra)
        return new


class LazyValue(object):
    """Some kind of "lazy evaluating" object."""

    def evaluate(self, obj, containers=()):
        """Compute the value, using the given object."""
        raise NotImplementedError("This is an abstract method.")


class SubFactoryWrapper(LazyValue):
    """Lazy wrapper around a SubFactory.

    Attributes:
        subfactory (declarations.SubFactory): the SubFactory being wrapped
        subfields (DeclarationDict): Default values to override when evaluating
            the SubFactory
        create (bool): whether to 'create' or 'build' the SubFactory.
    """

    def __init__(self, subfactory, subfields, create, *args, **kwargs):
        super(SubFactoryWrapper, self).__init__(*args, **kwargs)
        self.subfactory = subfactory
        self.subfields = subfields
        self.create = create

    def evaluate(self, obj, containers=()):
        expanded_containers = (obj,)
        if containers:
            expanded_containers += tuple(containers)
        return self.subfactory.evaluate(self.create, self.subfields,
            expanded_containers)


class OrderedDeclarationWrapper(LazyValue):
    """Lazy wrapper around an OrderedDeclaration.

    Attributes:
        declaration (declarations.OrderedDeclaration): the OrderedDeclaration
            being wrapped
        sequence (int): the sequence counter to use when evaluatin the
            declaration
    """

    def __init__(self, declaration, sequence, *args, **kwargs):
        super(OrderedDeclarationWrapper, self).__init__(*args, **kwargs)
        self.declaration = declaration
        self.sequence = sequence

    def evaluate(self, obj, containers=()):
        """Lazily evaluate the attached OrderedDeclaration.

        Args:
            obj (LazyStub): the object being built
            containers (object list): the chain of containers of the object
                being built, its immediate holder being first.
        """
        return self.declaration.evaluate(self.sequence, obj, containers)


class AttributeBuilder(object):
    """Builds attributes from a factory and extra data.

    Attributes:
        factory (base.Factory): the Factory for which attributes are being
            built
        _attrs (DeclarationDict): the attribute declarations for the factory
        _subfields (dict): dict mapping an attribute name to a dict of
            overridden default values for the related SubFactory.
    """

    def __init__(self, factory, extra=None, *args, **kwargs):
        super(AttributeBuilder, self).__init__(*args, **kwargs)

        if not extra:
            extra = {}

        self.factory = factory
        self._containers = extra.pop('__containers', None)
        self._attrs = factory.declarations(extra)
        self._subfields = self._extract_subfields()

    def _extract_subfields(self):
        """Extract the subfields from the declarations list."""
        sub_fields = {}
        for key in list(self._attrs):
            if ATTR_SPLITTER in key:
                # Trying to define a default of a subfactory
                cls_name, attr_name = key.split(ATTR_SPLITTER, 1)
                if cls_name in self._attrs:
                    sub_fields.setdefault(cls_name, {})[attr_name] = self._attrs.pop(key)
        return sub_fields

    def build(self, create):
        """Build a dictionary of attributes.

        Args:
            create (bool): whether to 'build' or 'create' the subfactories.
        """
        # Setup factory sequence.
        self.factory.sequence = self.factory._generate_next_sequence()

        # Parse attribute declarations, wrapping SubFactory and
        # OrderedDeclaration.
        wrapped_attrs = {}
        for k, v in self._attrs.iteritems():
            if isinstance(v, declarations.SubFactory):
                v = SubFactoryWrapper(v, self._subfields.get(k, {}), create)
            elif isinstance(v, declarations.OrderedDeclaration):
                v = OrderedDeclarationWrapper(v, self.factory.sequence)
            wrapped_attrs[k] = v

        return LazyStub(wrapped_attrs, containers=self._containers).__fill__()


class StubObject(object):
    """A generic container."""
    pass
