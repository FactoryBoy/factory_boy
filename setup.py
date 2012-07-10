#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Remember to change in factory/__init__.py as well!
VERSION = '1.1.5'


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
    packages=find_packages(),
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
    use_2to3=True,
    test_suite='factory.tests',
)
