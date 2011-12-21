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

from declarations import OrderedDeclaration, SubFactory


ATTR_SPLITTER = '__'


class CyclicDefinitionError(Exception):
    """Raised when cyclic definition were found."""


class LazyStub(object):
    """A generic container that allows for getting but not setting of attributes.

    Attributes are set at initialization time."""

    initialized = False

    def __init__(self, attrs):
        self.__attrs = attrs
        self.__values = {}
        self.__pending = []
        self.initialized = True

    def __fill__(self):
        res = {}
        for attr in self.__attrs:
            res[attr] = getattr(self, attr)
        return res

    def __getattr__(self, name):
        if name in self.__pending:
            raise CyclicDefinitionError(
                    "Cyclic lazy attribute definition for %s. Current cycle is %r." %
                    (name, self.__pending))
        elif name in self.__values:
            return self.__values[name]
        elif name in self.__attrs:
            val = self.__attrs[name]
            if isinstance(val, LazyValue):
                self.__pending.append(name)
                val = val.evaluate(self)
                assert name == self.__pending.pop()
            self.__values[name] = val
            return val
        else:
            raise AttributeError(
                "The parameter %s is unknown. Evaluated attributes are %r, definitions are %r." % (name, self.__values, self.__attrs))


    def __setattr__(self, name, value):
        if not self.initialized:
            return super(LazyStub, self).__setattr__(name, value)
        else:
            raise AttributeError('Setting of object attributes is not allowed')


class DeclarationDict(dict):
    def update_with_public(self, d):
        """Updates the DeclarationDict from a class definition dict.

        Takes into account all public attributes and OrderedDeclaration
        instances; ignores all attributes starting with '_'.

        Returns a dict containing all remaining elements.
        """
        remaining = {}
        for k, v in d.iteritems():
            if k.startswith('_') and not isinstance(v, OrderedDeclaration):
                remaining[k] = v
            else:
                self[k] = v
        return remaining

    def copy(self, extra=None):
        new = DeclarationDict()
        new.update(self)
        if extra:
            new.update(extra)
        return new


class LazyValue(object):
    def evaluate(self, obj):
        raise NotImplementedError("This is an abstract method.")


class SubFactoryWrapper(LazyValue):
    def __init__(self, subfactory, subfields, create):
        self.subfactory = subfactory
        self.subfields = subfields
        self.create = create

    def evaluate(self, obj):
        return self.subfactory.evaluate(self.create, self.subfields)


class OrderedDeclarationWrapper(LazyValue):
    def __init__(self, declaration, sequence):
        self.declaration = declaration
        self.sequence = sequence

    def evaluate(self, obj):
        return self.declaration.evaluate(self.sequence, obj)


class AttributeBuilder(object):
    """Builds attributes from a factory and extra data."""

    def __init__(self, factory, extra=None):
        if not extra:
            extra = {}
        self.factory = factory
        self._attrs = factory.declarations(extra)
        self._subfields = self._extract_subfields()

    def _extract_subfields(self):
        sub_fields = {}
        for key in list(self._attrs):
            if ATTR_SPLITTER in key:
                cls_name, attr_name = key.split(ATTR_SPLITTER, 1)
                if cls_name in self._attrs:
                    sub_fields.setdefault(cls_name, {})[attr_name] = self._attrs.pop(key)
        return sub_fields

    def build(self, create):
        self.factory.sequence = self.factory._generate_next_sequence()

        wrapped_attrs = {}
        for k, v in self._attrs.iteritems():
            if isinstance(v, SubFactory):
                v = SubFactoryWrapper(v, self._subfields.get(k, {}), create)
            elif isinstance(v, OrderedDeclaration):
                v = OrderedDeclarationWrapper(v, self.factory.sequence)
            wrapped_attrs[k] = v

        stub = LazyStub(wrapped_attrs)
        return stub.__fill__()


class StubObject(object):
    """A generic container."""

    pass
