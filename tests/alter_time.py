#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This code is in the public domain
# Author: Raphaël Barrois


from __future__ import print_function

import datetime
from .compat import mock


real_datetime_class = datetime.datetime

def mock_datetime_now(target, datetime_module):
    """Override ``datetime.datetime.now()`` with a custom target value.

    This creates a new datetime.datetime class, and alters its now()/utcnow()
    methods.

    Returns:
        A mock.patch context, can be used as a decorator or in a with.
    """

    # See http://bugs.python.org/msg68532
    # And http://docs.python.org/reference/datamodel.html#customizing-instance-and-subclass-checks
    class DatetimeSubclassMeta(type):
        """We need to customize the __instancecheck__ method for isinstance().

        This must be performed at a metaclass level.
        """

        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_datetime_class)

    class BaseMockedDatetime(real_datetime_class):
        @classmethod
        def now(cls, tz=None):
            return target.replace(tzinfo=tz)

        @classmethod
        def utcnow(cls):
            return target

    # Python2 & Python3-compatible metaclass
    MockedDatetime = DatetimeSubclassMeta('datetime', (BaseMockedDatetime,), {})

    return mock.patch.object(datetime_module, 'datetime', MockedDatetime)

real_date_class = datetime.date

def mock_date_today(target, datetime_module):
    """Override ``datetime.date.today()`` with a custom target value.

    This creates a new datetime.date class, and alters its today() method.

    Returns:
        A mock.patch context, can be used as a decorator or in a with.
    """

    # See http://bugs.python.org/msg68532
    # And http://docs.python.org/reference/datamodel.html#customizing-instance-and-subclass-checks
    class DateSubclassMeta(type):
        """We need to customize the __instancecheck__ method for isinstance().

        This must be performed at a metaclass level.
        """

        @classmethod
        def __instancecheck__(mcs, obj):
            return isinstance(obj, real_date_class)

    class BaseMockedDate(real_date_class):
        @classmethod
        def today(cls):
            return target

    # Python2 & Python3-compatible metaclass
    MockedDate = DateSubclassMeta('date', (BaseMockedDate,), {})

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


if __name__ == '__main__':  # pragma: no cover
    main()
