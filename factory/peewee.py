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
from peewee import fn
from playhouse.test_utils import test_database

from . import base


class PeeweeModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    ABSTRACT_FACTORY = True

    @classmethod
    def _setup_next_sequence(cls, *args, **kwargs):
        """Compute the next available PK, based on the 'pk' database field."""
        db = cls.FACTORY_DATABASE
        model = cls.FACTORY_FOR
        pk = getattr(model, model._meta.primary_key.name)
        with test_database(db, (model,), create_tables=False):
            max_pk = model.select(
                model, fn.Max(pk).alias('maxpk')
            ).limit(1).execute()
            max_pk = [mp.maxpk for mp in max_pk][0]
        if isinstance(max_pk, int):
            return max_pk + 1 if max_pk else 1
        else:
            return 1

    @classmethod
    def _create(cls, target_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        db = cls.FACTORY_DATABASE
        with test_database(db, (target_class,), create_tables=False):
            obj = target_class.create(**kwargs)
        return obj
