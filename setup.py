from setuptools import setup
import massmedia

try:
    long_desc = open('README').read()
except OSError:
    long_desc = ''

try:
    reqs = open('requirements.txt').read()
except OSError:
    reqs = ''

setup(
    name = "django-massmedia",
    version = massmedia.get_version(),
    url = 'http://opensource.washingtontimes.com/projects/django-massmedia/',
    author = 'Justin Quick',
    description = 'Allows for site staff can upload and edit the media files through the site, and the filesystem is maintained in the background.',
    long_description = long_desc,
    packages = ['massmedia'],
    include_package_data=True,
    install_requires = reqs,
)
