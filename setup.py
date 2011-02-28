#!/usr/bin/env python
import os
from setuptools import setup
import massmedia
try:
    long_desc = open(os.path.join(os.path.dirname(__file__),'README')).read()
except (IOError, OSError):
    long_desc = ''

try:
    reqs = open(os.path.join(os.path.dirname(__file__),'requirements.txt')).read()
except (IOError, OSError):
    reqs = ''

setup(
    name = "django-massmedia",
    version = massmedia.get_version(),
    url = 'http://github.com/washingtontimes/django-massmedia',
    author = 'Justin Quick',
    author_email = 'jquick@washingtontimes.com',
    description = 'Allows for site staff can upload and edit the media files through the site, and the filesystem is maintained in the background.',
    long_description = long_desc,
    packages = ['massmedia','massmedia.templatetags','massmedia.management','massmedia.management.commands'],
    package_data={'massmedia': [
        'templates/*.html',
        'templates/*/*.html',
        'templates/*/*/*.html',
        'templates/*/*/*/*.html',
        ]},
    include_package_data=True,
    install_requires = reqs,
)