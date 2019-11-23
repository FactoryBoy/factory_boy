#!/usr/bin/env python
# -*- coding: utf-8 -*-

import codecs
import os

from setuptools import setup

root_dir = os.path.abspath(os.path.dirname(__file__))


setup(
    name='factory_boy',
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
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: Implementation :: PyPy",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
)
