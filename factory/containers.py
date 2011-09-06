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

from declarations import OrderedDeclaration, SubFactory


ATTR_SPLITTER = '__'

class ObjectParamsWrapper(object):
    """A generic container that allows for getting but not setting of attributes.

    Attributes are set at initialization time."""

    initialized = False

    def __init__(self, attrs):
        self.attrs = attrs
        self.initialized = True

    def __setattr__(self, name, value):
        if not self.initialized:
            return super(ObjectParamsWrapper, self).__setattr__(name, value)
        else:
            raise AttributeError('Setting of object attributes is not allowed')

    def __getattr__(self, name):
        try:
            return self.attrs[name]
        except KeyError:
            raise AttributeError("The param '{0}' does not exist. Perhaps your declarations are out of order?".format(name))


class OrderedDict(object):
    def __init__(self, **kwargs):
        self._order = {}
        self._values = {}
        for k, v in kwargs.iteritems():
            self[k] = v

    def __contains__(self, key):
        return key in self._values

    def __getitem__(self, key):
        return self._values[key]

    def __setitem__(self, key, val):
        if key in self:
            del self[key]
        self._values[key] = val
        self._order[val.order] = key

    def __delitem__(self, key):
        self.pop(key)

    def pop(self, key):
        val = self._values.pop(key)
        del self._order[val.order]
        return val

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        order = sorted(self._order.keys())
        for i in order:
            key = self._order[i]
            yield (key, self._values[key])

    def __iter__(self):
        order = sorted(self._order.keys())
        for i in order:
            yield self._order[i]


class DeclarationDict(object):
    """Holds a dict of declarations, keeping OrderedDeclaration at the end."""
    def __init__(self, extra=None):
        if not extra:
            extra = {}
        self._ordered = OrderedDict()
        self._unordered = {}
        self.update(extra)

    def __setitem__(self, key, value):
        if key in self:
            del self[key]

        if isinstance(value, OrderedDeclaration):
            self._ordered[key] = value
        else:
            self._unordered[key] = value

    def __getitem__(self, key):
        """Try in _unordered first, then in _ordered."""
        try:
            return self._unordered[key]
        except KeyError:
            return self._ordered[key]

    def __delitem__(self, key):
        if key in self._unordered:
            del self._unordered[key]
        else:
            del self._ordered[key]

    def pop(self, key, *args):
        assert len(args) <= 1
        try:
            return self._unordered.pop(key)
        except KeyError:
            return self._ordered.pop(key, *args)

    def update(self, d):
        for k in d:
            self[k] = d[k]

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

    def __contains__(self, key):
        return key in self._unordered or key in self._ordered

    def items(self):
        return list(self.iteritems())

    def iteritems(self):
        for pair in self._unordered.iteritems():
            yield pair
        for pair in self._ordered.iteritems():
            yield pair

    def __iter__(self):
        for k in self._unordered:
            yield k
        for k in self._ordered:
            yield k


class AttributeBuilder(object):
    """Builds attributes from a factory and extra data."""

    def __init__(self, factory, extra=None):
        if not extra:
            extra = {}
        self.factory = factory
        self._attrs = factory.declarations(extra)
        self._subfield = self._extract_subfields()

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

        attributes = {}
        for key, val in self._attrs.iteritems():
            if isinstance(val, SubFactory):
                val = val.evaluate(self.factory, create, self._subfield.get(key, {}))
            elif isinstance(val, OrderedDeclaration):
                wrapper = ObjectParamsWrapper(attributes)
                val = val.evaluate(self.factory, wrapper)
            attributes[key] = val

        return attributes


class StubObject(object):
    """A generic container."""

    pass
