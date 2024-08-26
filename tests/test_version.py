# Copyright: See the LICENSE file.

import pathlib
import unittest

import factory

SETUP_CFG_VERSION_PREFIX = "version ="


class VersionTestCase(unittest.TestCase):
    def get_setupcfg_version(self):
        setup_cfg_path = pathlib.Path(__file__).parent.parent / "setup.cfg"
        with setup_cfg_path.open("r") as f:
            for line in f:
                if line.startswith(SETUP_CFG_VERSION_PREFIX):
                    return line[len(SETUP_CFG_VERSION_PREFIX):].strip()

    def test_version(self):
        self.assertEqual(factory.__version__, self.get_setupcfg_version())
