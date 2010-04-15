from setuptools import setup
import os
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
    url = 'http://opensource.washingtontimes.com/projects/django-massmedia/',
    author = 'Justin Quick',
    author_email = 'jquick@washingtontimes.com',
    description = 'Allows for site staff can upload and edit the media files through the site, and the filesystem is maintained in the background.',
    long_description = long_desc,
    packages = ['massmedia'],
    include_package_data=True,
    install_requires = reqs,
    dependency_links=[
        'http://opensource.washingtontimes.com/static/dist/IPTCInfo-1.9.5-1.tar.gz#md5=4d08413881d9bdb3c9c9466bb2bee7a4',
    ]
)
