from django.conf import settings
import warnings

DEFAULT_SETTINGS = {
    "IMAGE_EXTS": ('bmp','gif','ico','cur','jpg','jpeg','pcx','png','psd','tga','tiff','wmf','xcf','bmp','wmf','apm','emf'),
    "VIDEO_EXTS": ('asf','wmv','flv','mov','mpeg','mpg','mpe','vob','qt','mp4','m4v','rm','avi','ogm'),
    "AUDIO_EXTS": ('asf','aif','aiff','aifc','flac','au','snd','mid','midi','mpa','m4a','mp1','mp2','mp3','ra','xm','wav','ogg'),
    "FLASH_EXTS": ('swf',),
    "DOC_EXTS": ('pdf','xls','doc'),
    "INFO_QUALITY": 1.0, # Information quality for parsing metadata (0.0=fastest, 1.0=best, and default is 0.5)
    "THUMB_SIZE": (200,200), # Size of thumbnail to take for the admin preview
    "EXTRA_MIME_TYPES": {'.flv':'video/x-flv',}, # Extra mime types to monkey patch to mimetypes.types_map
    "FS_TEMPLATES": True, # Template mode, either off the fs (1) or through the admin (0)
    "IMPORT_LOCAL_TMP_DIR": '',
    "MOGRIFY_KEY": settings.SECRET_KEY,
    "USE_TAGGING": False,
}

DEFAULT_SETTINGS.update(getattr(settings, 'MASSMEDIA_SETTINGS', {}))

# How to store the files. The ``settings.DEFAULT_FILE_STORAGE`` is used for all media types
# unless overridden by another setting.
#
# Should be a string in the format: 'module.Class'
# **Default:** 'django.core.files.storage.FileSystemStorage'
STORAGE = {
    'DEFAULT': settings.DEFAULT_FILE_STORAGE,
    'IMAGE': settings.DEFAULT_FILE_STORAGE,
    'VIDEO': settings.DEFAULT_FILE_STORAGE,
    'AUDIO': settings.DEFAULT_FILE_STORAGE,
    'FLASH': settings.DEFAULT_FILE_STORAGE,
    'DOC': settings.DEFAULT_FILE_STORAGE
}

STORAGE.update(getattr(settings, 'MASSMEDIA_STORAGE', {}))

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
        'PASSWORD': '',},
}

user_services = getattr(settings, 'MASSMEDIA_SERVICES', {})
for key, val in user_services.items():
    if key in SERVICES:
        SERVICES[key].update(val)
    else:
        SERVICES[key] = val

if hasattr(settings, "MMEDIA_IMAGE_EXTS"):
    DEFAULT_SETTINGS["IMAGE_EXTS"] = getattr(settings, 'MMEDIA_IMAGE_EXTS')
    warnings.warn(
        "settings.MMEDIA_IMAGE_EXTS is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_VIDEO_EXTS'):
    DEFAULT_SETTINGS["VIDEO_EXTS"] = getattr(settings, 'MMEDIA_VIDEO_EXTS')
    warnings.warn(
        "settings.MMEDIA_VIDEO_EXTS is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_AUDIO_EXTS'):
    DEFAULT_SETTINGS["AUDIO_EXTS"] = getattr(settings, 'MMEDIA_AUDIO_EXTS')
    warnings.warn(
        "settings.MMEDIA_AUDIO_EXTS is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_FLASH_EXTS'):
    DEFAULT_SETTINGS["FLASH_EXTS"] = getattr(settings, 'MMEDIA_FLASH_EXTS')
    warnings.warn(
        "settings.MMEDIA_FLASH_EXTS is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_DOC_EXTS'):
    DEFAULT_SETTINGS["DOC_EXTS"] = getattr(settings, 'MMEDIA_DOC_EXTS')
    warnings.warn(
        "settings.MMEDIA_DOC_EXTS is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_INFO_QUALITY'):
    DEFAULT_SETTINGS["INFO_QUALITY"] = getattr(settings, 'MMEDIA_INFO_QUALITY')
    warnings.warn(
        "settings.MMEDIA_INFO_QUALITY is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_THUMB_SIZE'):
    DEFAULT_SETTINGS["THUMB_SIZE"] = getattr(settings, 'MMEDIA_THUMB_SIZE')
    warnings.warn(
        "settings.MMEDIA_THUMB_SIZE is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_EXTRA_MIME_TYPES'):
    DEFAULT_SETTINGS["EXTRA_MIME_TYPES"] = getattr(settings, 'MMEDIA_EXTRA_MIME_TYPES')
    warnings.warn(
        "settings.MMEDIA_EXTRA_MIME_TYPES is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_FS_TEMPLATES'):
    DEFAULT_SETTINGS["FS_TEMPLATES"] = getattr(settings, 'MMEDIA_FS_TEMPLATES')
    warnings.warn(
        "settings.MMEDIA_FS_TEMPLATES is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_LOCAL_IMPORT_TMP_DIR'):
    DEFAULT_SETTINGS["LOCAL_IMPORT_TMP_DIR"] = getattr(settings, 'MMEDIA_LOCAL_IMPORT_TMP_DIR')
    warnings.warn(
        "settings.MMEDIA_FS_TEMPLATES is deprecated; use settings.MASSMEDIA_SETTINGS instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_DEFAULT_STORAGE'):
    STORAGE["DEFAULT"] = getattr(settings, 'MMEDIA_DEFAULT_STORAGE')
    warnings.warn(
        "settings.MMEDIA_DEFAULT_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_IMAGE_STORAGE'):
    STORAGE["IMAGE"] = getattr(settings, 'MMEDIA_IMAGE_STORAGE')
    warnings.warn(
        "settings.MMEDIA_IMAGE_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_VIDEO_STORAGE'):
    STORAGE["VIDEO"] = getattr(settings, 'MMEDIA_VIDEO_STORAGE')
    warnings.warn(
        "settings.MMEDIA_VIDEO_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_AUDIO_STORAGE'):
    STORAGE["AUDIO"] = getattr(settings, 'MMEDIA_AUDIO_STORAGE')
    warnings.warn(
        "settings.MMEDIA_AUDIO_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_FLASH_STORAGE'):
    STORAGE["FLASH"] = getattr(settings, 'MMEDIA_FLASH_STORAGE')
    warnings.warn(
        "settings.MMEDIA_FLASH_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_DOC_STORAGE'):
    STORAGE["DOC"] = getattr(settings, 'MMEDIA_DOC_STORAGE')
    warnings.warn(
        "settings.MMEDIA_DOC_STORAGE is deprecated; use settings.MASSMEDIA_STORAGE instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'IMAGE_UPLOAD_TO'):
    UPLOAD_TO["IMAGE"] = getattr(settings, 'MMEDIA_IMAGE_UPLOAD_TO')
    warnings.warn(
        "settings.MMEDIA_IMAGE_UPLOAD_TO is deprecated; use settings.MASSMEDIA_UPLOAD_TO instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_VIDEO_UPLOAD_TO'):
    UPLOAD_TO["VIDEO"] = getattr(settings, 'MMEDIA_VIDEO_UPLOAD_TO')
    warnings.warn(
        "settings.MMEDIA_VIDEO_UPLOAD_TO is deprecated; use settings.MASSMEDIA_UPLOAD_TO instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_AUDIO_UPLOAD_TO'):
    UPLOAD_TO["AUDIO"] = getattr(settings, 'MMEDIA_AUDIO_UPLOAD_TO')
    warnings.warn(
        "settings.MMEDIA_AUDIO_UPLOAD_TO is deprecated; use settings.MASSMEDIA_UPLOAD_TO instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_FLASH_UPLOAD_TO'):
    UPLOAD_TO["FLASH"] = getattr(settings, 'MMEDIA_FLASH_UPLOAD_TO')
    warnings.warn(
        "settings.MMEDIA_FLASH_UPLOAD_TO is deprecated; use settings.MASSMEDIA_UPLOAD_TO instead.",
        PendingDeprecationWarning
    )

if hasattr(settings, 'MMEDIA_DOC_UPLOAD_TO'):
    UPLOAD_TO["DOC"] = getattr(settings, 'MMEDIA_DOC_UPLOAD_TO')
    warnings.warn(
        "settings.MMEDIA_DOC_UPLOAD_TO is deprecated; use settings.MASSMEDIA_UPLOAD_TO instead.",
        PendingDeprecationWarning
    )

globals().update(DEFAULT_SETTINGS)
globals().update([('%s_STORAGE' % key, val) for key, val in STORAGE.items()])
globals().update([('%s_UPLOAD_TO' % key, val) for key, val in UPLOAD_TO.items()])
