from distutils.core import setup

setup(
    name = "django-massmedia",
    version = '0.1',
    url = 'http://opensource.washingtontimes.com/projects/django-massmedia/',
    author = 'Justin Quick',
    description = 'Allows for site staff can upload and edit the media files through the site, and the filesystem is maintained in the background.',
    packages = ['massmedia']
)
