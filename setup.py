#!/usr/bin/env python

import os
import sys

try:
    from setuptools import setup, find_packages
except ImportError:
    from distutils.core import setup, find_packages

__author__ = 'Adam Miskiewicz <adam@bolsterlabs.com>'
__version__ = '0.1.0'

if sys.argv[-1] == 'publish':
    os.system('python setup.py sdist upload')
    sys.exit()

setup(
    name='django-social-stream',
    version=__version__,
    install_requires=[
        'twython==3.1.0',
        'jsonfield==0.9.19',
        'celery-pipelines>=0.1.0',
        'django-autoslug==1.7.1',
    ],
    author='Adam Miskiewicz',
    author_email='adam@bolsterlabs.com',
    license=open('LICENSE').read(),
    url='https://github.com/bolster/django-social-stream/tree/master',
    keywords='twitter search api tweet django stream facebook realtime',
    description='Djangoified Social Streamer (Twitter & Facebook)',
    long_description=open('README.rst').read() + '\n\n' + open('HISTORY.rst').read(),
    include_package_data=True,
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'tests.*']),
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Communications :: Chat',
        'Topic :: Internet'
    ]
)
