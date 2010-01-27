from django.conf import settings

# Valid media extensions, edit at your own risk
IMAGE_EXTS = getattr(settings, 'IMAGE_EXTS', ('bmp','gif','ico','cur','jpg','jpeg','pcx','png','psd','tga','tiff','wmf','xcf','bmp','wmf','apm','emf'))
VIDEO_EXTS = getattr(settings, 'VIDEO_EXTS', ('asf','wmv','flv','mov','mpeg','mpg','mpe','vob','qt','mp4','m4v','rm','avi','ogm'))
AUDIO_EXTS = getattr(settings, 'AUDIO_EXTS', ('asf','aif','aiff','aifc','flac','au','snd','mid','midi','mpa','m4a','mp1','mp2','mp3','ra','xm','wav','ogg'))
FLASH_EXTS = getattr(settings, 'FLASH_EXTS', ('swf',))
DOC_EXTS = getattr(settings, 'DOC_EXTS', ('pdf','xls','doc'))
                                          
# Information quality for parsing metadata (0.0=fastest, 1.0=best, and default is 0.5)
INFO_QUALITY = getattr(settings, 'INFO_QUALITY', 1.0)

# Size of thumbnail to take for the admin preview
THUMB_SIZE = getattr(settings, 'THUMB_SIZE', (100,80))

# Extra mime types to monkey patch to mimetypes.types_map
EXTRA_MIME_TYPES = getattr(settings, 'EXTRA_MIME_TYPES', {
    '.flv':'video/x-flv',
})

# Template mode, either off the fs (1) or through the admin (0)
TEMPLATE_MODE = getattr(settings, 'TEMPLATE_MODE', 1)

# Integration settings w/ Grab Networks videos
GRAB_API_KEY = getattr(settings, 'GRAB_API_KEY', None)
GRAB_API_URL = getattr(settings, 'GRAB_API_URL', 'http://wasabi_v0.grabnetworks.com/videos/')


IMPORT_LOCAL_TMP_DIR = getattr(settings, 'MM_LOCAL_IMPORT_TMP_DIR', '')