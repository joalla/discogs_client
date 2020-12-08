#!/usr/bin/env python

from setuptools import setup

setup(
        name='python3-discogs-client',
        version='2.3.5',
        description='Python API client for Discogs',
        long_description='This is an active fork of the official "Discogs API client for Python", which was deprecated by discogs.com as of June 2020. We think it is a very useful Python module and decided to continue maintaining it. Please visit: https://github.com/joalla/discogs_client for more information.',
        url='https://github.com/joalla/discogs_client',
        author='joalla',
        author_email='jt@peek-a-boo.at',
        test_suite='discogs_client.tests',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
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
            'oauthlib',
            ],
        packages=[
            'discogs_client',
            ],
        )
