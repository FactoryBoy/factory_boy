#!/usr/bin/python
# -*- coding: utf-8 -*-

from distutils.core import setup
from distutils import cmd

# Remember to change in factory/__init__.py as well!
VERSION = '1.1.1'


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
        import unittest
        if self.verbose:
            verbosity=1
        else:
            verbosity=0

        suite = unittest.TestLoader().loadTestsFromName(self.test_suite)

        unittest.TextTestRunner(verbosity=verbosity).run(suite)


setup(
    name='factory_boy',
    version=VERSION,
    description="A verstile test fixtures replacement based on thoughtbot's factory_girl for Ruby.",
    author='Mark Sandstrom',
    author_email='mark@deliciouslynerdy.com',
    maintainer='Raphaël Barrois',
    maintainer_email='raphael.barrois@polytechnique.org',
    url='http://github.com/rbarrois/factory_boy',
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
        'Topic :: Software Development :: Testing',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    cmdclass={'test': test},
)
