"""
Miscellaneous utility functions
"""

import os
from time import strftime
from django.template.defaultfilters import slugify


def is_image(filepath):
    """
    Test the extension against valid image extensions
    """
    from .settings import IMAGE_EXTS
    _, ext = os.path.splitext(filepath)
    ext = ext.replace(".", "")
    return ext in IMAGE_EXTS


def value_or_list(val):
    """
    If this is a 1-item list, give us the value, otherwise, keep the list
    """
    if len(val) == 1:
        return val[0]
    else:
        return val


def super_force_ascii(bad_string):
    """
    For unicode strings that are improperly encoded, 1. convert to latin-1 to
    make it a regular string, convert it back to a unicode string, assuming that
    the string is encoded using default windows encoding. Then return an ascii
    string using xmlcharrefreplace for oddball characters
    """
    output = u''
    for char in bad_string:
        try:
            if ord(char) > 127:
                if isinstance(char, unicode):
                    bs1 = char.encode('latin-1', 'ignore')
                else:
                    bs1 = char
                bs2 = bs1.decode('cp1252', 'ignore')
                output = u"%s%s" % (output, bs2)
            else:
                output = u"%s%s" % (output, char)
        except UnicodeDecodeError:
            continue
    return output.encode('ascii', 'xmlcharrefreplace')


def custom_upload_to(instance, filename):
    """
    Clean the initial file name and build a destination path based on
    settings as prefix_path
    """
    prefix_path = instance.prefix_path
    # Split and clean the filename with slugify
    filename = os.path.basename(filename)
    name, dot, extension = filename.rpartition('.')
    slug = slugify(name)
    clean_filename = '%s.%s' % (slug, extension.lower())
    # Build a destination path with previous cleaned string.
    destination_path = os.path.join(strftime(prefix_path), clean_filename)

    return destination_path
