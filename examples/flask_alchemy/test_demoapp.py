import os
import unittest
import tempfile

import demoapp
import demoapp_factories

class DemoAppTestCase(unittest.TestCase):

    def setUp(self):
        demoapp.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        demoapp.app.config['TESTING'] = True
        self.app = demoapp.app.test_client()
        self.db = demoapp.db
        self.db.create_all()

    def tearDown(self):
        self.db.drop_all()

    def test_user_factory(self):
        user = demoapp_factories.UserFactory()
        self.db.session.commit()
        self.assertIsNotNone(user.id)
        self.assertEqual(1, len(demoapp.User.query.all()))

    def test_userlog_factory(self):
        userlog = demoapp_factories.UserLogFactory()
        self.db.session.commit()
        self.assertIsNotNone(userlog.id)
        self.assertIsNotNone(userlog.user.id)
        self.assertEqual(1, len(demoapp.User.query.all()))
        self.assertEqual(1, len(demoapp.UserLog.query.all()))

if __name__ == '__main__':
    unittest.main()
