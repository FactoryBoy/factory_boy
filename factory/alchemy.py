# -*- coding: utf-8 -*-
# Copyright: See the LICENSE file.

from __future__ import unicode_literals

import warnings
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import NoResultFound

from . import base
from . import errors

SESSION_PERSISTENCE_COMMIT = 'commit'
SESSION_PERSISTENCE_FLUSH = 'flush'
VALID_SESSION_PERSISTENCE_TYPES = [
    None,
    SESSION_PERSISTENCE_COMMIT,
    SESSION_PERSISTENCE_FLUSH,
]


class SQLAlchemyOptions(base.FactoryOptions):
    def _check_sqlalchemy_session_persistence(self, meta, value):
        if value not in VALID_SESSION_PERSISTENCE_TYPES:
            raise TypeError(
                "%s.sqlalchemy_session_persistence must be one of %s, got %r" %
                (meta, VALID_SESSION_PERSISTENCE_TYPES, value)
            )

    def _check_force_flush(self, meta, value):
        if value:
            warnings.warn(
                "%(meta)s.force_flush has been deprecated as of 2.8.0 and will be removed in 3.0.0. "
                "Please set ``%(meta)s.sqlalchemy_session_persistence = 'flush'`` instead."
                % dict(meta=meta),
                DeprecationWarning,
                # Stacklevel:
                # declaration -> FactoryMetaClass.__new__ -> meta.contribute_to_class
                # -> meta._fill_from_meta -> option.apply -> option.checker
                stacklevel=6,
            )

    def _build_default_options(self):
        return super(SQLAlchemyOptions, self)._build_default_options() + [
            base.OptionDefault('get_or_create', (), inherit=True),
            base.OptionDefault('sqlalchemy_session', None, inherit=True),
            base.OptionDefault(
                'sqlalchemy_session_persistence',
                None,
                inherit=True,
                checker=self._check_sqlalchemy_session_persistence,
            ),

            # DEPRECATED as of 2.8.0, remove in 3.0.0
            base.OptionDefault(
                'force_flush',
                False,
                inherit=True,
                checker=self._check_force_flush,
            ),
        ]


class SQLAlchemyModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    _options_class = SQLAlchemyOptions

    class Meta:
        abstract = True

    @classmethod
    def _get_or_create(cls, model_class, *args, **kwargs):
        """Get or create an instance of the model."""

        session = cls._meta.sqlalchemy_session

        key_fields = {}
        for field in cls._meta.get_or_create:
            if field not in kwargs:
                raise errors.FactoryError(
                    "get_or_create - "
                    "Unable to find initialization value for '%s' in factory %s" %
                    (field, cls.__name__))
            key_fields[field] = kwargs.pop(field)

        try:
            instance = session.query(model_class).filter_by(**key_fields).one_or_none()
            if not instance:
                instance = model_class(*args, **key_fields)
                session.add(instance)
        except IntegrityError:
            try:
                instance = session.query(model_class).filter_by(**kwargs).one()
            except NoResultFound:
                raise ValueError(
                    "get_or_create - Unable to create a new object "
                    "due an IntegrityError raised based on "
                    "your model's uniqueness constraints. "
                    "DoesNotExist: Unable to find an existing object based on "
                    "the fields specified in your factory instance.")

        return instance

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session
        session_persistence = cls._meta.sqlalchemy_session_persistence
        if cls._meta.force_flush:
            session_persistence = SESSION_PERSISTENCE_FLUSH

        if session is None:
            raise RuntimeError("No session provided.")

        if cls._meta.get_or_create:
            obj = cls._get_or_create(model_class, *args, **kwargs)
        else:
            obj = model_class(*args, **kwargs)
            session.add(obj)

        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            session.commit()
        return obj
