# Copyright: See the LICENSE file.


"""Helpers for testing SQLAlchemy apps."""

from sqlalchemy import Column, Integer, Unicode, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker

session = scoped_session(sessionmaker())
engine = create_engine('sqlite://')
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


Base.metadata.create_all(engine)
