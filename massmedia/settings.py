from django.conf import settings

DEFAULT_SETTINGS = {
    "IMAGE_EXTS": ('bmp', 'gif', 'ico', 'cur', 'jpg', 'jpeg', 'pcx', 'png',
                   'psd', 'tga', 'tiff', 'wmf', 'xcf', 'bmp', 'wmf', 'apm',
                   'emf'),
    "VIDEO_EXTS": ('asf', 'wmv', 'flv', 'mov', 'mpeg', 'mpg', 'mpe', 'vob',
                   'qt', 'mp4', 'm4v', 'rm', 'avi', 'ogm'),
    "AUDIO_EXTS": ('asf', 'aif', 'aiff', 'aifc', 'flac', 'au', 'snd', 'mid',
                   'midi', 'mpa', 'm4a', 'mp1', 'mp2', 'mp3', 'ra', 'xm',
                   'wav', 'ogg'),
    "FLASH_EXTS": ('swf', ),
    "DOC_EXTS": ('pdf', 'xls', 'doc'),
    "INFO_QUALITY": 1.0,  # Information quality for parsing metadata (0.0=fastest, 1.0=best, and default is 0.5)
    "THUMB_SIZE": (200, 200),  # Size of thumbnail to take for the admin preview
    "EXTRA_MIME_TYPES": {'.flv': 'video/x-flv', },  # Extra mime types to monkey patch to mimetypes.types_map
    "FS_TEMPLATES": True,  # Template mode, either off the fs (1) or through the admin (0)
    "IMPORT_LOCAL_TMP_DIR": '',
    "TRANSMOGRIFY_KEY": getattr(settings, 'TRANSMOGRIFY_SECRET_KEY', settings.SECRET_KEY),
    'CONTENT_TYPE_CHOICES': (
        ('audio', 'Audio'),
        ('document', 'Document'),
        ('interactive', 'Interactive'),
        ('presentation', 'Presentation'),
        ('video', 'Video'),
    )
}

DEFAULT_SETTINGS.update(getattr(settings, 'MASSMEDIA_SETTINGS', {}))

# How to store the files. The ``settings.DEFAULT_FILE_STORAGE`` is used for all media types
# unless overridden by another setting.
#
# Should be a string in the format: 'module.Class'
# **Default:** 'django.core.files.storage.FileSystemStorage'
STORAGE = {
    'DEFAULT': settings.DEFAULT_FILE_STORAGE,
    'IMAGE': None,
    'VIDEO': None,
    'AUDIO': None,
    'FLASH': None,
    'DOC': None,
}

STORAGE.update(getattr(settings, 'MASSMEDIA_STORAGE', {}))
STORAGE['IMAGE'] = STORAGE['IMAGE'] or STORAGE['DEFAULT']
STORAGE['VIDEO'] = STORAGE['VIDEO'] or STORAGE['DEFAULT']
STORAGE['AUDIO'] = STORAGE['AUDIO'] or STORAGE['DEFAULT']
STORAGE['FLASH'] = STORAGE['FLASH'] or STORAGE['DEFAULT']
STORAGE['DOC'] = STORAGE['DOC'] or STORAGE['DEFAULT']


UPLOAD_TO = {
    'IMAGE': 'image/%Y/%m/%d',
    'THUMB': 'thumb/%Y/%m/%d',
    'VIDEO': 'video/%Y/%m/%d',
    'AUDIO': 'audio/%Y/%m/%d',
    'FLASH': 'flash/%Y/%m/%d',
    'DOC': 'misc/%Y/%m/%d',
}

UPLOAD_TO.update(getattr(settings, 'MASSMEDIA_UPLOAD_TO', {}))

SERVICES = {
    'YOUTUBE': {
        'EMAIL': '',
        'USERNAME': '',
        'PASSWORD': '',
    },
}

user_services = getattr(settings, 'MASSMEDIA_SERVICES', {})
for key, val in user_services.items():
    if key in SERVICES:
        SERVICES[key].update(val)
    else:
        SERVICES[key] = val


globals().update(DEFAULT_SETTINGS)
globals().update([('%s_STORAGE' % key, val) for key, val in STORAGE.items()])
globals().update([('%s_UPLOAD_TO' % key, val) for key, val in UPLOAD_TO.items()])
