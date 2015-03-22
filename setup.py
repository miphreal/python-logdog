#!/usr/bin/env python
import os
from setuptools import find_packages, setup

from logdog import (
    __version__ as version,
    __author__ as author,
    __email__ as author_email)


requires = [
    r.strip() for r in
    open(os.path.join(os.getcwd(), 'requirements.txt')).readlines()
]

setup(
    name='logdog',
    version=version,
    description='logs watching + webui',
    author=author,
    author_email=author_email,
    url='https://github.com/miphreal/python-logdog/',
    packages=find_packages(exclude=['tests']),
    scripts=['scripts/logdog'],
    install_requires=requires
)