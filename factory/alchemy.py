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

from . import base
import warnings

SESSION_PERSISTENCE_COMMIT = 'commit'
SESSION_PERSISTENCE_FLUSH = 'flush'
VALID_SESSION_PERSISTENCE_TYPES = [
    None,
    SESSION_PERSISTENCE_COMMIT,
    SESSION_PERSISTENCE_FLUSH,
]


class SQLAlchemyOptions(base.FactoryOptions):
    def _build_default_options(self):
        return super(SQLAlchemyOptions, self)._build_default_options() + [
            base.OptionDefault('sqlalchemy_session', None, inherit=True),
            base.OptionDefault('sqlalchemy_session_persistence', None, inherit=True),

            # DEPRECATED as of 2.8.0, remove in 3.0.0
            base.OptionDefault('force_flush', False, inherit=True),
        ]


class SQLAlchemyModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    _options_class = SQLAlchemyOptions

    class Meta:
        abstract = True

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if cls._meta.force_flush:
            session_persistence = SESSION_PERSISTENCE_FLUSH
            warnings.warn("force_flush has been deprecated as of 2.8.0 and will be removed in 3.0.0. Please use `sqlalchemy_session_persistence='flush'` insead.", DeprecationWarning)
        if session_persistence not in VALID_SESSION_PERSISTENCE_TYPES:
            raise TypeError(
                "'sqlalchemy_session_persistence' must be 'flush' or 'commit', got '%s'"
                % session_persistence
            )

        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == 'flush':
            session.flush()
        elif session_persistence == 'commit':
            session.commit()
        return obj
