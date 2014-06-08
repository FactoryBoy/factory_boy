# -*- coding: utf-8 -*-
# Copyright (c) 2013 Romain Commandé
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
from __future__ import absolute_import
import peewee

from . import base


class PeeweeOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super(PeeweeOptions, self)._build_default_options() + [
            base.OptionDefault('database', None, inherit=True),
        ]

        
class PeeweeModelFactory(base.Factory):
    """Factory for peewee models. """

    _options_class = PeeweeOptions
    class Meta:
        abstract = True

    _OLDSTYLE_ATTRIBUTES = base.Factory._OLDSTYLE_ATTRIBUTES.copy()
    _OLDSTYLE_ATTRIBUTES.update({
        'FACTORY_DATABASE': 'database',
    })

    @classmethod
    def _setup_next_sequence(cls, *args, **kwargs):
        """Compute the next available PK, based on the 'pk' database field."""
        db = cls._meta.database
        model = cls._meta.model
        pk = getattr(model, model._meta.primary_key.name)
        max_pk = model.select(
                model, peewee.fn.Max(pk).alias('maxpk')
            ).limit(1).execute()
        max_pk = [mp.maxpk for mp in max_pk][0]
        if isinstance(max_pk, int):
            return max_pk + 1 if max_pk else 1
        else:
            return 1

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        db = cls._meta.database
        obj = target_class.create(**kwargs)
        return obj
