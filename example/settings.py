# Django settings for example project.

DEBUG = True
TEMPLATE_DEBUG = DEBUG
import os, sys
APP = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
sys.path.append(APP)

ADMINS = (
    # ('Your Name', 'your_email@domain.com'),
)

MANAGERS = ADMINS

DATABASE_ENGINE = 'sqlite3'           # 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
DATABASE_NAME = 'dev.db'             # Or path to database file if using sqlite3.
DATABASE_USER = ''             # Not used with sqlite3.
DATABASE_PASSWORD = ''         # Not used with sqlite3.
DATABASE_HOST = ''             # Set to empty string for localhost. Not used with sqlite3.
DATABASE_PORT = ''             # Set to empty string for default. Not used with sqlite3.

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = 'America/Chicago'

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = 'en-us'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# Absolute path to the directory that holds media.
# Example: "/home/media/media.lawrence.com/"
MEDIA_ROOT = os.path.abspath(os.path.join('media'))

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash if there is a path component (optional in other cases).
# Examples: "http://media.lawrence.com", "http://example.com/media/"
MEDIA_URL = '/static/'

# URL prefix for admin media -- CSS, JavaScript and images. Make sure to use a
# trailing slash.
# Examples: "http://foo.com/media/", "/media/".
ADMIN_MEDIA_PREFIX = '/media/'

# Make this unique, and don't share it with anybody.
SECRET_KEY = 'g2_39yupn*6j4p*cg2%w643jiq-1n_annua*%i8+rq0dx9p=$n'

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.load_template_source',
    'django.template.loaders.app_directories.load_template_source',
#     'django.template.loaders.eggs.load_template_source',
)

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)

ROOT_URLCONF = 'example.urls'

TEMPLATE_DIRS = (
    # Put strings here, like "/home/html/django_templates" or "C:/www/django/templates".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    os.path.join(PROJECT_ROOT,'templates')
)

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'massmedia',
    'tagging',
    'django.contrib.flatpages',
    'tinymce',
    'testapp',
    #'south',
)

MMEDIA_IMAGE_STORAGE = 'media_storage.MediaStorage'

MASSMEDIA_SERVICES = {
    'YOUTUBE': {
        'EMAIL': '',
        'USERNAME': '',
        'PASSWORD': '',
    },
}

TINYMCE_DEFAULT_CONFIG = {
    'mode': "textareas",
    'theme': "advanced",
    'language': "en",
    'visual': True,
    'skin': "o2k7",
    'dialog_type': "modal",
    'object_resizing': True,
    'cleanup_on_startup': True,
    'forced_root_block': "p",
    'remove_trailing_nbsp': True,
    'theme_advanced_toolbar_location': "top",
    'theme_advanced_toolbar_align': "left",
    'theme_advanced_statusbar_location': "none",
    'theme_advanced_buttons1': "formatselect,bold,italic,underline,bullist,numlist,undo,redo,link,unlink,image,mmimage,code,fullscreen,pasteword,media,charmap",
    'theme_advanced_buttons2': "",
    'theme_advanced_buttons3': "",
    'theme_advanced_path': False,
    'theme_advanced_blockformats': "p,h2,h3,h4,h5,h6",
    'width': '700',
    'height': '200',
    'plugins': "safari,mmimage,advlink,fullscreen,visualchars,paste,media,template,searchreplace,inlinepopups",
    'advimage_update_dimensions_onchange': True,
    'relative_urls': False,
    'valid_elements' : "" +"-p[]," + "a[href|target=_blank|class]," +"-strong/-b," +"-em/-i," +"-u," + "-ol," + "-ul," + "-li," + "br," + "img[class|src|alt=|width|height]," + "-h2,-h3,-h4," + "-pre," +"-code," + "-div",
    'extended_valid_elements': "" + 
        "a[name|class|href|target|title|onclick]," + 
        "img[class|src|border=0|alt|title|hspace|vspace|width|height|align|onmouseover|onmouseout|name]," + 
        "br[clearfix]," + 
        "-p[class|style]," + 
        "h2[class<clearfix],h3[class<clearfix],h4[class<clearfix]," + 
        "ul[class<clearfix],ol[class<clearfix]," + 
        "div[class|style],"
}
TINYMCE_FILEBROWSER = True
TINYMCE_JS_URL = os.path.join(MEDIA_URL, "js/tiny_mce/tiny_mce_src.js")
