#!/usr/bin/env python

from setuptools import setup

setup(
        name='python3-discogs-client',
        version='2.3.1',
        description='Python API client for Discogs',
        url='https://github.com/joalla/discogs_client',
        author='joalla',
        author_email='jt@peek-a-boo.at',
        test_suite='discogs_client.tests',
        classifiers=[
            'Development Status :: 7 - Inactive',
            'Environment :: Console',
            'License :: OSI Approved :: BSD License',
            'Natural Language :: English',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Topic :: Communications',
            'Topic :: Utilities',
            ],
        install_requires=[
            'requests',
            'six',
            'oauthlib',
            ],
        packages=[
            'discogs_client',
            ],
        )
