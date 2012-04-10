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

#: String for splitting an attribute name into a
#: (subfactory_name, subfactory_field) tuple.
ATTR_SPLITTER = '__'

def extract_dict(prefix, kwargs, pop=True):
    """Extracts all values beginning with a given prefix from a dict.

    Can either 'pop' or 'get' them;

    Args:
        prefix (str): the prefix to use for lookups
        kwargs (dict): the dict from which values should be extracted
        pop (bool): whether to use pop (True) or get (False)

    Returns:
        A new dict, containing values from kwargs and beginning with
            prefix + ATTR_SPLITTER. That full prefix is removed from the keys
            of the returned dict.
    """
    prefix = prefix + ATTR_SPLITTER
    extracted = {}
    for key in list(kwargs.keys()):
        if key.startswith(prefix):
            new_key = key[len(prefix):]
            if pop:
                value = kwargs.pop(key)
            else:
                value = kwargs[key]
            extracted[new_key] = value
    return extracted


def multi_extract_dict(prefixes, kwargs, pop=True):
    """Extracts all values from a given list of prefixes."""
    results = {}
    for prefix in sorted(prefixes, key=lambda prefix: (-len(prefix), prefix)):
        extracted = extract_dict(prefix, kwargs, pop=pop)
        results[prefix] = extracted
    return results
