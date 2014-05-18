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
from sqlalchemy.sql.functions import max

from . import base


class SQLAlchemyOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super(SQLAlchemyOptions, self)._build_default_options() + [
            base.OptionDefault('sqlalchemy_session', None, inherit=True),
        ]


class SQLAlchemyModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    _options_class = SQLAlchemyOptions
    class Meta:
        abstract = True

    _OLDSTYLE_ATTRIBUTES = base.Factory._OLDSTYLE_ATTRIBUTES.copy()
    _OLDSTYLE_ATTRIBUTES.update({
        'FACTORY_SESSION': 'sqlalchemy_session',
    })

    @classmethod
    def _setup_next_sequence(cls, *args, **kwargs):
        """Compute the next available PK, based on the 'pk' database field."""
        session = cls._meta.sqlalchemy_session
        model = cls._meta.model
        pk = getattr(model, model.__mapper__.primary_key[0].name)
        max_pk = session.query(max(pk)).one()[0]
        if isinstance(max_pk, int):
            return max_pk + 1 if max_pk else 1
        else:
            return 1

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session
        obj = model_class(*args, **kwargs)
        session.add(obj)
        return obj
