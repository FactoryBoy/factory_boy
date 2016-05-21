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

import collections

from . import compat

#: String for splitting an attribute name into a
#: (subfactory_name, subfactory_field) tuple.
ATTR_SPLITTER = '__'


def extract_dict(prefix, kwargs, pop=True, exclude=()):
    """Extracts all values beginning with a given prefix from a dict.

    Can either 'pop' or 'get' them;

    Args:
        prefix (str): the prefix to use for lookups
        kwargs (dict): the dict from which values should be extracted; WILL BE MODIFIED.
        pop (bool): whether to use pop (True) or get (False)
        exclude (iterable): list of prefixed keys that shouldn't be extracted

    Returns:
        A new dict, containing values from kwargs and beginning with
            prefix + ATTR_SPLITTER. That full prefix is removed from the keys
            of the returned dict.
    """
    prefix = prefix + ATTR_SPLITTER
    extracted = {}

    for key in list(kwargs):
        if key in exclude:
            continue

        if key.startswith(prefix):
            new_key = key[len(prefix):]
            if pop:
                value = kwargs.pop(key)
            else:
                value = kwargs[key]
            extracted[new_key] = value
    return extracted


def multi_extract_dict(prefixes, kwargs, pop=True, exclude=()):
    """Extracts all values from a given list of prefixes.

    Extraction will start with longer prefixes.

    Args:
        prefixes (str list): the prefixes to use for lookups
        kwargs (dict): the dict from which values should be extracted; WILL BE MODIFIED.
        pop (bool): whether to use pop (True) or get (False)
        exclude (iterable): list of prefixed keys that shouldn't be extracted

    Returns:
        dict(str => dict): a dict mapping each prefix to the dict of extracted
            key/value.
    """
    results = {}
    exclude = list(exclude)
    for prefix in sorted(prefixes, key=lambda x: -len(x)):
        extracted = extract_dict(prefix, kwargs, pop=pop, exclude=exclude)
        results[prefix] = extracted
        exclude.extend(
            ['%s%s%s' % (prefix, ATTR_SPLITTER, key) for key in extracted])

    return results


def import_object(module_name, attribute_name):
    """Import an object from its absolute path.

    Example:
        >>> import_object('datetime', 'datetime')
        <type 'datetime.datetime'>
    """
    # Py2 compatibility: force str (i.e bytes) when importing.
    module = __import__(str(module_name), {}, {}, [str(attribute_name)], 0)
    return getattr(module, str(attribute_name))


def _safe_repr(obj):
    try:
        return log_repr(obj)
    except Exception:
        return '<bad_repr object at %s>' % id(obj)


class log_pprint(object):
    """Helper for properly printing args / kwargs passed to an object.

    Since it is only used with factory.debug(), the computation is
    performed lazily.
    """
    __slots__ = ['args', 'kwargs']

    def __init__(self, args=(), kwargs=None):
        self.args = args
        self.kwargs = kwargs or {}

    def __repr__(self):
        return repr(str(self))

    def __str__(self):
        return ', '.join(
            [_safe_repr(arg) for arg in self.args] +
            [
                '%s=%s' % (key, _safe_repr(value))
                for key, value in self.kwargs.items()
            ]
        )


def log_repr(obj):
    """Generate a text-compatible repr of an object.

    Some projects have a tendency to generate bytes-style repr in Python2.
    """
    return compat.force_text(repr(obj))


class ResetableIterator(object):
    """An iterator wrapper that can be 'reset()' to its start."""
    def __init__(self, iterator, **kwargs):
        super(ResetableIterator, self).__init__(**kwargs)
        self.iterator = iter(iterator)
        self.past_elements = collections.deque()
        self.next_elements = collections.deque()

    def __iter__(self):
        while True:
            if self.next_elements:
                yield self.next_elements.popleft()
            else:
                value = next(self.iterator)
                self.past_elements.append(value)
                yield value

    def reset(self):
        self.next_elements.clear()
        self.next_elements.extend(self.past_elements)
