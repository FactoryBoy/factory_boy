#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os
import re

from setuptools import setup

root_dir = os.path.abspath(os.path.dirname(__file__))


def get_version(package_name):
    version_re = re.compile(r"^__version__ = [\"']([\w_.-]+)[\"']$")
    package_components = package_name.split('.')
    init_path = os.path.join(root_dir, *(package_components + ['__init__.py']))
    with codecs.open(init_path, 'r', 'utf-8') as f:
        for line in f:
            match = version_re.match(line[:-1])
            if match:
                return match.groups()[0]
    return '0.1.0'


PACKAGE = 'factory'


setup(
    name='factory_boy',
    version=get_version(PACKAGE),
    description="A versatile test fixtures replacement based on thoughtbot's factory_bot for Ruby.",
    long_description=codecs.open(os.path.join(root_dir, 'README.rst'), 'r', 'utf-8').read(),
    author='Mark Sandstrom',
    author_email='mark@deliciouslynerdy.com',
    maintainer='Raphaël Barrois',
    maintainer_email='raphael.barrois+fboy@polytechnique.org',
    url='https://github.com/FactoryBoy/factory_boy',
    keywords=['factory_boy', 'factory', 'fixtures'],
    packages=['factory'],
    zip_safe=False,
    license='MIT',
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*, !=3.4.*",
    install_requires=[
        'Faker>=0.7.0',
    ],
    setup_requires=[
        'setuptools>=0.8',
    ],
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Django",
        "Framework :: Django :: 1.11",
        "Framework :: Django :: 2.1",
        "Framework :: Django :: 2.2",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
