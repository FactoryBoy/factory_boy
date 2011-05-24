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
    '''A generic container that allows for getting but not setting of attributes.

    Attributes are set at initialization time.'''

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


class OrderedDeclarationDict(object):
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

class DeclarationsHolder(object):
    """Holds all declarations, ordered and unordered."""

    def __init__(self, defaults=None):
        if not defaults:
            defaults = {}
        self._ordered = OrderedDeclarationDict()
        self._unordered = {}
        self.update_base(defaults)

    def update_base(self, attrs):
        """Updates the DeclarationsHolder from a class definition.

        Takes into account all public attributes and OrderedDeclaration
        instances; ignores all attributes starting with '_'.

        Returns a dict containing all remaining elements.
        """
        remaining = {}
        for key, value in attrs.iteritems():
            if isinstance(value, OrderedDeclaration):
                self._ordered[key] = value
            elif not key.startswith('_'):
                self._unordered[key] = value
            else:
                remaining[key] = value
        return remaining

    def __contains__(self, key):
        return key in self._ordered or key in self._unordered

    def __getitem__(self, key):
        try:
            return self._unordered[key]
        except KeyError:
            return self._ordered[key]

    def iteritems(self):
        for pair in self._unordered.iteritems():
            yield pair
        for pair in self._ordered.iteritems():
            yield pair

    def items(self):
        return list(self.iteritems())

    def build_attributes(self, factory, create=False, extra=None):
        """Build the list of attributes based on class attributes."""
        if not extra:
            extra = {}

        factory.sequence = factory._generate_next_sequence()

        attributes = {}
        sub_fields = {}
        for key in list(extra.keys()):
            if ATTR_SPLITTER in key:
                cls_name, attr_name = key.split(ATTR_SPLITTER, 1)
                if cls_name in self:
                    sub_fields.setdefault(cls_name, {})[attr_name] = extra.pop(key)

        # For fields in _unordered, use the value from extra if any; otherwise,
        # use the default value.
        for key, value in self._unordered.iteritems():
            attributes[key] = extra.get(key, value)
        for key, value in self._ordered.iteritems():
            if key in extra:
                attributes[key] = extra[key]
            else:
                if isinstance(value, SubFactory):
                    new_value = value.evaluate(factory, create,
                                               sub_fields.get(key, {}))
                else:
                    wrapper = ObjectParamsWrapper(attributes)
                    new_value = value.evaluate(factory, wrapper)
                attributes[key] = new_value
        attributes.update(extra)
        return attributes

class StubObject(object):
    '''A generic container.'''

    pass
