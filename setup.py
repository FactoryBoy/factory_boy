#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import re
import sys
from distutils.core import setup
from distutils import cmd

root = os.path.abspath(os.path.dirname(__file__))

def get_version(*module_dir_components):
    version_re = re.compile(r"^__version__ = ['\"](.*)['\"]$")
    module_root = os.path.join(root, *module_dir_components)
    module_init = os.path.join(module_root, '__init__.py')
    with open(module_init, 'r') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'

VERSION = get_version('factory')


class test(cmd.Command):
    """Run the tests for this package."""
    command_name = 'test'
    description = 'run the tests associated with the package'

    user_options = [
        ('test-suite=', None, "A test suite to run (defaults to 'tests')"),
    ]

    def initialize_options(self):
        self.test_runner = None
        self.test_suite = None

    def finalize_options(self):
        self.ensure_string('test_suite', 'tests')

    def run(self):
        """Run the test suite."""
        try:
            import unittest2 as unittest
        except ImportError:
            import unittest

        if self.verbose:
            verbosity=1
        else:
            verbosity=0

        suite = unittest.TestLoader().loadTestsFromName(self.test_suite)

        result = unittest.TextTestRunner(verbosity=verbosity).run(suite)
        if not result.wasSuccessful():
            sys.exit(1)


setup(
    name='factory_boy',
    version=VERSION,
    description="A verstile test fixtures replacement based on thoughtbot's factory_girl for Ruby.",
    author='Mark Sandstrom',
    author_email='mark@deliciouslynerdy.com',
    maintainer='Raphaël Barrois',
    maintainer_email='raphael.barrois@polytechnique.org',
    url='https://github.com/rbarrois/factory_boy',
    keywords=['factory_boy', 'factory', 'fixtures'],
    packages=['factory'],
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Framework :: Django',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'test': test},
)
