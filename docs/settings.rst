.. _settings:

======================
Configuration Settings
======================


MMEDIA_IMAGE_EXTS
=================

Recognized extensions for image files. It should be a ``list`` or ``tuple`` of ``string``\ s without the leading period. **Default:** ::

	MMEDIA_IMAGE_EXTS = ('bmp','gif','ico','cur','jpg','jpeg','pcx',
	                     'png','psd','tga','tiff','wmf','xcf','bmp',
	                     'wmf','apm','emf')

MMEDIA_VIDEO_EXTS
=================

Recognized extensions for video files. It should be a ``list`` or ``tuple`` of ``string``\ s without the leading period. **Default:** ::

	MMEDIA_VIDEO_EXTS = ('asf','wmv','flv','mov','mpeg','mpg','mpe','vob',
	                     'qt','mp4','m4v','rm','avi','ogm')

MMEDIA_AUDIO_EXTS
=================

Recognized extensions for audio files. It should be a ``list`` or ``tuple`` of ``string``\ s without the leading period. **Default:** ::


	MMEDIA_AUDIO_EXTS = ('asf','aif','aiff','aifc','flac','au','snd','mid',
	                     'midi','mpa','m4a','mp1','mp2','mp3','ra','xm',
	                     'wav','ogg')

MMEDIA_FLASH_EXTS
=================

Recognized extensions for SWF files. It should be a ``list`` or ``tuple`` of ``string``\ s without the leading period. **Default:** ::

	MMEDIA_FLASH_EXTS = ('swf',)


MMEDIA_DOC_EXTS
===============

Recognized extensions for generic document files. It should be a ``list`` or ``tuple`` of ``string``\ s without the leading period. **Default:** ::

	MMEDIA_DOC_EXTS = ('pdf','xls','doc')


MMEDIA_INFO_QUALITY
===================

The ``hachoir_metadata`` library allows you to specify how it parses metadata, from 0.0 (fastest) to 1.0 (best quality). **Default:** ::

	MMEDIA_INFO_QUALITY = 1.0


MMEDIA_THUMB_SIZE
=================

The size of automatically generated thumbnails for images. It is a two integer tuple for width and height. The default is 100px wide by 80px high. **Default:** ::

	MMEDIA_THUMB_SIZE = (100, 80)


MMEDIA_EXTRA_MIME_TYPES
=======================

The Python standard library includes a MIME types map of file extensions to MIME type. However, this map may be incomplete. This setting extends the default mapping. It is a ``dict`` of dot-extensions mapped to MIME type. **Default:** ::

	MMEDIA_EXTRA_MIME_TYPES = {'.flv':'video/x-flv',}


MMEDIA_FS_TEMPLATES
===================

There are two ways to manage the templates used to render content: via the admin or through files on the computer's file system. If this setting is ``False``\ , there will be a ``MediaTemplate`` model for managing the templates by MIME type. By default, this setting is ``True`` and templates are managed through the path ``massmedia/``\ . Massmedia looks in a hierarchy for the correct template. For example, an image with a MIME type of ``image/jpeg``\ ::

	/massmedia/image/jpeg.html
	/massmedia/image/generic.html
	/massmedia/generic.html

Where it first looks for the most specific template, and then falls back to more generic templates. **Default:** ::

	MMEDIA_FS_TEMPLATES = True


MMEDIA_LOCAL_IMPORT_TMP_DIR
===========================

TODO


GRAB_API_KEY
============

In order to import items from Grab Network, you need an API key.


GRAB_API_URL
============

In order to import items from Grab Network, you'll also need an API URL.