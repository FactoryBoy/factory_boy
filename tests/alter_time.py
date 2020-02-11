#!/usr/bin/env python
# This code is in the public domain
# Author: Raphaël Barrois


import datetime
from unittest import mock

real_datetime_class = datetime.datetime


def mock_datetime_now(target, datetime_module):
    """Override ``datetime.datetime.now()`` with a custom target value.

    This creates a new datetime.datetime class, and alters its now()/utcnow()
    methods.

    Returns:
        A mock.patch context, can be used as a decorator or in a with.
    """

    # See https://bugs.python.org/msg68532
    # And https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks
    class DatetimeSubclassMeta(type):
        """We need to customize the __instancecheck__ method for isinstance().

        This must be performed at a metaclass level.
        """

        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class MockedDatetime(real_datetime_class, metaclass=DatetimeSubclassMeta):
        @classmethod
        def now(cls, tz=None):
            return target.replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return target

    return mock.patch.object(datetime_module, 'datetime', MockedDatetime)


real_date_class = datetime.date


def mock_date_today(target, datetime_module):
    """Override ``datetime.date.today()`` with a custom target value.

    This creates a new datetime.date class, and alters its today() method.

    Returns:
        A mock.patch context, can be used as a decorator or in a with.
    """

    # See https://bugs.python.org/msg68532
    # And https://docs.python.org/3/reference/datamodel.html#customizing-instance-and-subclass-checks
    class DateSubclassMeta(type):
        """We need to customize the __instancecheck__ method for isinstance().

        This must be performed at a metaclass level.
        """

        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_date_class)

    class MockedDate(real_date_class, metaclass=DateSubclassMeta):
        @classmethod
        def today(cls):
            return target

    return mock.patch.object(datetime_module, 'date', MockedDate)


def main():  # pragma: no cover
    """Run a couple of tests"""
    target_dt = real_datetime_class(2009, 1, 1)
    target_date = real_date_class(2009, 1, 1)

    print("Entering mock")
    with mock_datetime_now(target_dt, datetime):
        print("- now                       ->", datetime.datetime.now())
        print("- isinstance(now, dt)       ->", isinstance(datetime.datetime.now(), datetime.datetime))
        print("- isinstance(target, dt)    ->", isinstance(target_dt, datetime.datetime))

    with mock_date_today(target_date, datetime):
        print("- today                     ->", datetime.date.today())
        print("- isinstance(now, date)     ->", isinstance(datetime.date.today(), datetime.date))
        print("- isinstance(target, date)  ->", isinstance(target_date, datetime.date))

    print("Outside mock")
    print("- now                       ->", datetime.datetime.now())
    print("- isinstance(now, dt)       ->", isinstance(datetime.datetime.now(), datetime.datetime))
    print("- isinstance(target, dt)    ->", isinstance(target_dt, datetime.datetime))

    print("- today                     ->", datetime.date.today())
    print("- isinstance(now, date)     ->", isinstance(datetime.date.today(), datetime.date))
    print("- isinstance(target, date)  ->", isinstance(target_date, datetime.date))
