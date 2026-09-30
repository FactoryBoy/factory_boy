# Copyright: See the LICENSE file.

import copy
import dataclasses
import pickle
import unittest

import factory
from factory import SKIP


@dataclasses.dataclass
class Server:
    host: str
    port: int = 80


class ServerFactory(factory.Factory):
    class Meta:
        model = Server

    host = "localhost"
    port = 8080


class SkipTestCase(unittest.TestCase):
    def test_declared(self):
        """A field declared as SKIP is left out of the generated dict."""

        class ConfigFactory(factory.DictFactory):
            host = "localhost"
            debug = SKIP

        self.assertEqual(ConfigFactory(), {"host": "localhost"})

    def test_call_time(self):
        """A call-time SKIP drops a declared field."""

        class ConfigFactory(factory.DictFactory):
            host = "localhost"
            debug = True

        self.assertEqual(ConfigFactory(debug=SKIP), {"host": "localhost"})

    def test_model_default(self):
        """A model falls back to its own default for a skipped argument."""
        self.assertEqual(ServerFactory(port=SKIP), Server(host="localhost", port=80))

    def test_copied_kwargs(self):
        """SKIP stays the same object through deepcopy and pickle."""
        kwargs = {"port": SKIP}
        for clone in (copy.deepcopy(kwargs), pickle.loads(pickle.dumps(kwargs))):
            self.assertEqual(ServerFactory(**clone), Server(host="localhost", port=80))

    def test_repr(self):
        self.assertEqual(repr(SKIP), "factory.SKIP")
