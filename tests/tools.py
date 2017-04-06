# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.


import functools
import warnings


def disable_warnings(fun):
    @functools.wraps(fun)
    def decorated(*args, **kwargs):
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            return fun(*args, **kwargs)
    return decorated


