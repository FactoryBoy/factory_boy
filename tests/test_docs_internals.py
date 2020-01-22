# Copyright (c) 2011-2015 Raphaël Barrois
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
"""Tests for the docs/internals module."""

import datetime
import unittest

import factory
import factory.fuzzy


class User:
    def __init__(
        self,
        username,
        full_name,
        is_active=True,
        is_superuser=False,
        is_staff=False,
        creation_date=None,
        deactivation_date=None,
    ):
        self.username = username
        self.full_name = full_name
        self.is_active = is_active
        self.is_superuser = is_superuser
        self.is_staff = is_staff
        self.creation_date = creation_date
        self.deactivation_date = deactivation_date
        self.logs = []

    def log(self, action, timestamp):
        UserLog(user=self, action=action, timestamp=timestamp)


class UserLog:

    ACTIONS = ['create', 'update', 'disable']

    def __init__(self, user, action, timestamp):
        self.user = user
        self.action = action
        self.timestamp = timestamp

        user.logs.append(self)


class UserLogFactory(factory.Factory):
    class Meta:
        model = UserLog

    user = factory.SubFactory('test_docs_internals.UserFactory')
    timestamp = factory.fuzzy.FuzzyDateTime(
        datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
    )
    action = factory.Iterator(UserLog.ACTIONS)


class UserFactory(factory.Factory):
    class Meta:
        model = User

    class Params:
        # Allow us to quickly enable staff/superuser flags
        superuser = factory.Trait(
            is_superuser=True,
            is_staff=True,
        )
        # Meta parameter handling all 'enabled'-related fields
        enabled = True

    # Classic fields
    username = factory.Faker('user_name')
    full_name = factory.Faker('name')
    creation_date = factory.fuzzy.FuzzyDateTime(
        datetime.datetime(2000, 1, 1, tzinfo=datetime.timezone.utc),
        datetime.datetime(2015, 12, 31, 20, tzinfo=datetime.timezone.utc)
    )

    # Conditional flags
    is_active = factory.SelfAttribute('enabled')
    deactivation_date = factory.Maybe(
        'enabled',
        None,
        factory.fuzzy.FuzzyDateTime(
            datetime.datetime.now().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=10),
            datetime.datetime.now().replace(tzinfo=datetime.timezone.utc) - datetime.timedelta(days=1),
        ),
    )

    # Related logs
    creation_log = factory.RelatedFactory(
        UserLogFactory,
        factory_related_name='user',
        action='create',
        timestamp=factory.SelfAttribute('user.creation_date'),
    )


class DocsInternalsTests(unittest.TestCase):
    def test_simple_usage(self):
        user = UserFactory()

        # Default user should be active, not super
        self.assertTrue(user.is_active)
        self.assertFalse(user.is_superuser)
        self.assertFalse(user.is_staff)

        # We should have one log
        self.assertEqual(1, len(user.logs))
        # And it should be a 'create' action linked to the user's creation_date
        self.assertEqual('create', user.logs[0].action)
        self.assertEqual(user, user.logs[0].user)
        self.assertEqual(user.creation_date, user.logs[0].timestamp)
