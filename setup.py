# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

import ClearMap

with open('README.rst') as fptr:
    readme = fptr.read()

with open('LICENSE.txt') as fptr:
    license = fptr.read()

setup(
    name             = ClearMap.__title__,
    version          = ClearMap.__version__,
    description      = readme.split('\n')[0],
    long_description = readme,
    author           = "Christoph Kirst",
    author_email     = 'ckirst@rockefeller.edu',
    url              = 'https://www.idisco.info/',
    license          = license,
    packages         = find_packages(exclude=('tests', 'docs')),
    classifiers=(
        'Development Status :: 1- Beta',
        'Intended Audience :: Science/Research',
        'Natural Language :: English',
        'License :: GNU GENERAL PUBLIC LICENSE Version 3 2.0',
        'Programming Language :: Python',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ),
)