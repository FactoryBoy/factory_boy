# Copyright: See the LICENSE file.

from . import base, enums

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

    def _build_default_options(self):
        return super()._build_default_options() + [
            base.OptionDefault('sqlalchemy_session', None, inherit=True),
            base.OptionDefault(
                'sqlalchemy_session_persistence',
                None,
                inherit=True,
                checker=self._check_sqlalchemy_session_persistence,
            ),
        ]

    def _get_renamed_options(self):
        """Map an obsolete option to its new name."""
        return super()._get_renamed_options() + [
            base.OptionRenamed(
                origin='sqlalchemy_get_or_create',
                target='unique_constraints',
                transform=lambda fields: [[field] for field in fields],
            ),
        ]


class SQLAlchemyModelFactory(base.Factory):
    """Factory for SQLAlchemy models. """

    _options_class = SQLAlchemyOptions

    class Meta:
        abstract = True

    @classmethod
    def _lookup(cls, model_class, strategy, fields):
        if strategy != enums.CREATE_STRATEGY:
            return
        session = cls._meta.sqlalchemy_session
        if session is None:
            raise RuntimeError("No session provided.")
        return session.query(model_class).filter_by(**fields).one_or_none()

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create an instance of the model, and save it to the database."""
        session = cls._meta.sqlalchemy_session

        if session is None:
            raise RuntimeError("No session provided.")
        return cls._save(model_class, session, *args, **kwargs)

    @classmethod
    def _save(cls, model_class, session, *args, **kwargs):
        session_persistence = cls._meta.sqlalchemy_session_persistence

        obj = model_class(*args, **kwargs)
        session.add(obj)
        if session_persistence == SESSION_PERSISTENCE_FLUSH:
            session.flush()
        elif session_persistence == SESSION_PERSISTENCE_COMMIT:
            session.commit()
        return obj
