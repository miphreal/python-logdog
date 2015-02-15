#!/usr/bin/env python
from distutils.core import setup
import os

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
    versionversion,
    description='logs watching + webui',
    author=author,
    author_email=author_email,
    url='https://github.com/miphreal/python-logdog/',
    packages=['logdog'],
    scripts=['scripts/logdog'],
    install_requires=requires
)