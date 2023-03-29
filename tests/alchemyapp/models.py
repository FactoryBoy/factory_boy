# Copyright: See the LICENSE file.


"""Helpers for testing SQLAlchemy apps."""
import os

from sqlalchemy import Column, Integer, Unicode, create_engine
from sqlalchemy.orm import declarative_base, scoped_session, sessionmaker

try:
    import psycopg2  # noqa: F401
    USING_POSTGRES = True
except ImportError:
    try:
        # pypy does not support `psycopg2` or `psycopg2-binary`
        # This is a package that only gets installed with pypy, and it needs to be
        # initialized for it to work properly. It mimic `psycopg2` 1-to-1
        from psycopg2cffi import compat
        compat.register()
        USING_POSTGRES = True
    except ImportError:
        USING_POSTGRES = False

if USING_POSTGRES:
    pg_database = 'alch_' + os.environ.get('POSTGRES_DATABASE', 'factory_boy_test')
    pg_user = os.environ.get('POSTGRES_USER', 'postgres')
    pg_password = os.environ.get('POSTGRES_PASSWORD', 'password')
    pg_host = os.environ.get('POSTGRES_HOST', 'localhost')
    pg_port = os.environ.get('POSTGRES_PORT', '5432')
    engine_name = f'postgresql+psycopg2://{pg_user}:{pg_password}@{pg_host}:{pg_port}/{pg_database}'
else:
    engine_name = 'sqlite://'

session = scoped_session(sessionmaker())
engine = create_engine(engine_name)
session.configure(bind=engine)
Base = declarative_base()


class StandardModel(Base):
    __tablename__ = 'StandardModelTable'

    id = Column(Integer(), primary_key=True)
    foo = Column(Unicode(20))


class MultiFieldModel(Base):
    __tablename__ = 'MultiFieldModelTable'

    id = Column(Integer(), primary_key=True)
    foo = Column(Unicode(20))
    slug = Column(Unicode(20), unique=True)


class MultifieldUniqueModel(Base):
    __tablename__ = 'MultiFieldUniqueModelTable'

    id = Column(Integer(), primary_key=True)
    slug = Column(Unicode(20), unique=True)
    text = Column(Unicode(20), unique=True)
    title = Column(Unicode(20), unique=True)


class NonIntegerPk(Base):
    __tablename__ = 'NonIntegerPk'

    id = Column(Unicode(20), primary_key=True)


class SpecialFieldModel(Base):
    __tablename__ = 'SpecialFieldModelTable'

    id = Column(Integer(), primary_key=True)
    session = Column(Unicode(20))
