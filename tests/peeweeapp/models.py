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


"""Helpers for testing peewee apps."""

from peewee import (
    Model, PrimaryKeyField, SqliteDatabase, CharField
)
from playhouse.test_utils import test_database


database = SqliteDatabase(':memory:', autocommit=False)

database.connect()


class StandardModel(Model):
    id = PrimaryKeyField()
    foo = CharField(max_length=20)


class NonIntegerPk(Model):
    id = CharField(primary_key=True)


with test_database(database, (StandardModel, NonIntegerPk,), create_tables=False):
    if StandardModel.table_exists():
        StandardModel.drop_table()
    StandardModel.create_table()
    if NonIntegerPk.table_exists():
        NonIntegerPk.drop_table()
    NonIntegerPk.create_table()
