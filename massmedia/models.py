import re
import os
import zipfile
try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.db import models
from django.template.defaultfilters import slugify
from django.template.loader import get_template
from django.template import Template
from django.utils.translation import ugettext as _

from .settings import (IMAGE_STORAGE, VIDEO_STORAGE, AUDIO_STORAGE,
    FLASH_STORAGE, DOC_STORAGE, IMAGE_UPLOAD_TO, THUMB_UPLOAD_TO, THUMB_SIZE,
    VIDEO_UPLOAD_TO, DOC_UPLOAD_TO, AUDIO_UPLOAD_TO, FLASH_UPLOAD_TO,
    IMAGE_EXTS, VIDEO_EXTS, AUDIO_EXTS, FLASH_EXTS, DOC_EXTS, CONTENT_TYPE_CHOICES,
    TRANSMOGRIFY_KEY)


from base_models import Media, PublicMediaManager
from massmedia import resize

try:
    from iptcinfo import IPTCInfo
    HAS_IPTC = True
except ImportError:
    HAS_IPTC = False

from PIL import Image as PilImage

IMAGE_STORAGE = get_storage_class(IMAGE_STORAGE)
VIDEO_STORAGE = get_storage_class(VIDEO_STORAGE)
AUDIO_STORAGE = get_storage_class(AUDIO_STORAGE)
FLASH_STORAGE = get_storage_class(FLASH_STORAGE)
DOC_STORAGE = get_storage_class(DOC_STORAGE)


def generate_url(url, action_string):
    from hashlib import sha1
    security_hash = sha1(action_string + TRANSMOGRIFY_KEY).hexdigest()
    base_url, ext = os.path.splitext(url)

    return "%s%s%s?%s" % (base_url, action_string, ext, security_hash)


class Image(Media):
    """
    We are using a File field instead of Image field because the Image field will
    cause a problem if the file doesn't exist and you merely access the record.
    """
    file = models.FileField(
        upload_to=IMAGE_UPLOAD_TO,
        blank=True,
        null=True,
        storage=IMAGE_STORAGE())
    thumbnail = models.ImageField(
        upload_to=THUMB_UPLOAD_TO,
        blank=True,
        null=True,
        width_field='thumb_width',
        height_field='thumb_height',
        editable=False,
        storage=IMAGE_STORAGE())
    thumb_width = models.IntegerField(blank=True, null=True, editable=False)
    thumb_height = models.IntegerField(blank=True, null=True, editable=False)
    original = models.ForeignKey(
        'self',
        related_name="variations",
        blank=True, null=True)

    ACCESSOR_MAPPINGS = (
        (re.compile('get_([0-9]+x[0-9]+)_url'), '_get_SIZE_url'),
        (re.compile('get_(.*)_size'), '_get_SIZE_size')
    )

    def save(self, *args, **kwargs):
        generate_thumb = (self.id is None or self.thumbnail is None)
        super(Image, self).save(*args, **kwargs)
        if generate_thumb:
            self._generate_thumbnail()

    def _generate_thumbnail(self):
        """
        Be aware that this function handle very badly remote backends such as
        s3. You can add in your save() method something like::

            if 's3boto' in settings.DEFAULT_FILE_STORAGE:
                self.external_url = self.image.file.url
        """
        image = None
        if self.external_url:
            import urllib
            filepath, headers = urllib.urlretrieve(self.external_url)
            image = PilImage.open(filepath)
            filename = os.path.basename(filepath)
        elif self.file:
            image = PilImage.open(self.file.path)
            filename = os.path.basename(self.file.name)
        if image is None:
            return
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image.thumbnail(THUMB_SIZE, PilImage.ANTIALIAS)

        destination = StringIO()
        image.save(destination, format='JPEG')
        destination.seek(0)

        self.thumbnail.save(filename, ContentFile(destination.read()))

    def smart_fit(self, width=20000, height=20000):
        """
        Given a width, height or both, it will return the width and height to
        fit in the given area.
        """
        return resize.fit_to_box((self.width, self.height), width, height)

    def smart_fill(self, width, height):
        """
        Fill the image to the given width and height
        """
        orig_dims = (self.width, self.height)
        dest_dims = (width, height)
        wanted_ratio = ((width * 1.0) / height) * 1000
        try:
            crop = self.custom_sizes.get_for_dimensions(width, height)[0]
            if abs(wanted_ratio - self.ratio) < abs(wanted_ratio - crop.ratio):
                raise IndexError
            crop_dims = crop.crop_bounding_box
        except IndexError:
            crop_dims = None
        return resize.fill_box(orig_dims, dest_dims, crop_dims, resize.CENTER)

    def _get_SIZE_size(self, size):  # NOQA
        width, height = map(int, size.split('x'))
        wanted_ratio = ((width * 1.0) / height) * 1000
        try:
            crop = self.custom_sizes.get_for_dimensions(width=width, height=height)[0]
            if abs(wanted_ratio - self.ratio) < abs(wanted_ratio - crop.ratio):
                raise IndexError
            width = crop.width
            height = crop.height
        except IndexError:
            width = self.width
            height = self.height
        return self.smart_fit(width, height)

    def _get_SIZE_url(self, size):  # NOQA
        """
        Return the URL for the given size (dddxddd)
        """
        width, height = map(int, size.split('x'))
        if self.width is None or self.height is None:
            return ''
        crop_dims = self.smart_fill(width, height)
        if crop_dims == (0, 0, self.width, self.height) or crop_dims is None:
            processors = ["_r%dx%d" % (width, height), ]
        else:
            processors = [
                '_c%d-%d-%d-%d' % crop_dims,
                "_r%dx%d" % (width, height),
            ]
        return generate_url(self.file.url, "".join(processors))

    def get_size(self, size):
        if 'x' in size:
            func_name = "get_%s_size" % size
            func = getattr(self, func_name, lambda: None)
            return func()

        return None

    def get_url(self, size):
        if 'x' in size:
            func_name = "get_%s_url" % size
            func = getattr(self, func_name, lambda: '')
            return func()

        return ''

    def get_purge_url(self):
        from hashlib import sha1

        security_hash = sha1('PURGE' + TRANSMOGRIFY_KEY).hexdigest()
        return "%s?%s" % (self.image.url, security_hash)

    @property
    def ratio(self):
        return ((self.width * 1.0) / self.height) * 1000

    @property
    def media_url(self):
        return self.external_url or self.file.url

    def _get_raw_metadata(self, path):
        data = super(Image, self)._get_raw_metadata(path)
        if HAS_IPTC:
            try:
                data.update(IPTCInfo(path).__dict__['_data'])
            except:
                pass
        return data

    def parse_metadata(self):
        super(Image, self).parse_metadata()

        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']
        self.one_off_author = self.metadata['Author'] or self.metadata['80'] or ''
        if isinstance(self.one_off_author, (tuple, list)):
            self.one_off_author = ", ".join(self.one_off_author)
        if not self.caption:
            self.caption = self.metadata['120'] or self.metadata['Title'] or ''
        tags = []
        tags.extend(self.metadata["15"] or [])
        tags.extend(self.metadata["20"] or [])
        tags.extend(self.metadata["25"] or [])

    def __getattr__(self, name):
        """
        Delegate to size accessor methods if it is such a call
        """
        from django.utils.functional import curry

        method_name = name
        for reg, fnct_name in self.ACCESSOR_MAPPINGS:
            m = reg.match(method_name)
            if m:
                groups = m.groups()
                size = groups[0]
                if not size:
                    size = groups[-1]
                fnct = getattr(self, fnct_name)
                return curry(fnct, size)
        raise AttributeError('No method %s' % method_name)


class CustomSizeManager(models.Manager):
    """
    Custom manager that has a shortcut for selecting a custom crop/size given a
    width and height
    """
    def get_for_dimensions(self, width, height, ratio_tolerance=300):
        ratio = int((width * 1.0 / height) * 1000)
        qs = self.get_queryset().filter(width__gte=width)
        qs = qs.filter(height__gte=height)
        if ratio_tolerance:
            qs = qs.filter(ratio__lte=ratio + ratio_tolerance)
            qs = qs.filter(ratio__gte=max(ratio - ratio_tolerance, 0))
        return qs.order_by('-ratio')


class ImageCustomSize(models.Model):
    """
    Represents a non-photologue managed photo associated with an NGPhoto
    """
    image = models.ForeignKey(
        Image,
        verbose_name=_('original image'),
        related_name='custom_sizes')
    width = models.PositiveIntegerField(_('thumbnail width'), default=0,)
    height = models.PositiveIntegerField(_('thumbnail height'), default=0,)
    crop_x = models.PositiveIntegerField(_('crop x'), default=0,)
    crop_y = models.PositiveIntegerField(_('crop y'), default=0,)
    crop_w = models.PositiveIntegerField(_('crop width'), default=0,)
    crop_h = models.PositiveIntegerField(_('crop height'), default=0,)
    ratio = models.PositiveIntegerField(_('aspect ratio'), default=0,)

    objects = CustomSizeManager()

    def __unicode__(self):
        return "%s: crop %s x %s" % (self.image.title, self.width, self.height)

    def url(self, custom_width=None, custom_height=None):
        processors = ['_c%d-%d-%d-%d' % self.crop_bounding_box]
        width = custom_width or self.width
        height = custom_height or self.height
        if width != self.crop_w or height != self.crop_h:
            # We need to resize the image, the crop is not exact
            processors.append('_l%dx%d-fff' % (width, height))

        return generate_url(self.image.file.url, "".join(processors))

    @property
    def crop_bounding_box(self):
        """
        Return a tuple of (left, top, right, bottom)
        Assumes origin (0, 0) is top left
        """
        return (self.crop_x, self.crop_y,
                self.crop_x + self.crop_w, self.crop_y + self.crop_h)


class Embed(Media):
    code = models.TextField(
        _("Embed Code"),
        help_text=_("Embed HTML source code"),
        blank=True, null=True)

    content_type = models.CharField(
        _("Content Type"),
        max_length=50,
        blank=True, null=True,
        help_text=_("The type of content this contains. For display purposes."),
        choices=CONTENT_TYPE_CHOICES)

    @property
    def media_url(self):
        return self.external_url

    def get_template(self, template_type):
        return get_template('massmedia/embed.html')


class Video(Media):
    """
    A local or remote video file
    """
    file = models.FileField(
        upload_to=VIDEO_UPLOAD_TO,
        blank=True,
        null=True,
        storage=VIDEO_STORAGE())
    thumbnail = models.ForeignKey(
        Image,
        null=True, blank=True)

    def thumb(self):
        if self.thumbnail:
            return self.thumbnail.thumb()
        else:
            return ''
    thumb.allow_tags = True
    thumb.short_description = _("Thumbnail")

    @property
    def media_url(self):
        return self.external_url or self.file.url

    def parse_metadata(self):
        super(Video, self).parse_metadata()
        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']


class Audio(Media):
    """
    An audio file
    """
    file = models.FileField(
        upload_to=AUDIO_UPLOAD_TO,
        blank=True, null=True,
        storage=AUDIO_STORAGE())

    class Meta:
        verbose_name = _("audio clip")
        verbose_name_plural = _("audio clips")

    @property
    def media_url(self):
        return self.external_url or self.file.url


class Flash(Media):
    """
    A flash SWF file to be played in a custom player
    """
    file = models.FileField(
        upload_to=FLASH_UPLOAD_TO,
        blank=True, null=True,
        storage=FLASH_STORAGE())

    content_type = models.CharField(
        _("Content Type"),
        max_length=50,
        blank=True, null=True,
        help_text=_("The type of content this contains. For display purposes."),
        choices=CONTENT_TYPE_CHOICES)

    class Meta:
        verbose_name = _("SWF File")
        verbose_name_plural = _("SWF Files")

    @property
    def media_url(self):
        return self.external_url or self.file.url


class Document(Media):
    """
    A generic file
    """
    file = models.FileField(
        upload_to=DOC_UPLOAD_TO,
        blank=True,
        null=True,
        storage=DOC_STORAGE())

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    @property
    def media_url(self):
        return self.external_url or self.file.url


EXT_TO_MODEL_MAP = {}
for ext in IMAGE_EXTS:
    EXT_TO_MODEL_MAP[ext] = Image

for ext in VIDEO_EXTS:
    EXT_TO_MODEL_MAP[ext] = Video

for ext in AUDIO_EXTS:
    EXT_TO_MODEL_MAP[ext] = Audio

for ext in FLASH_EXTS:
    EXT_TO_MODEL_MAP[ext] = Flash

for ext in DOC_EXTS:
    EXT_TO_MODEL_MAP[ext] = Document


class Collection(models.Model):
    """
    An arbitrary collection of massmedia items
    """
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    zip_file = models.FileField(
        _("Media files in a .zip"),
        upload_to='tmp',
        blank=True, null=True,
        help_text=_("Select a .zip file of media to upload into a the Collection."))
    external_url = models.URLField(
        blank=True,
        help_text=_("Pull content from an external source. Supported: YouTube"))
    public = models.BooleanField(
        help_text=_("this collection is publicly available"),
        default=True)
    site = models.ForeignKey(Site)

    objects = PublicMediaManager()

    class Meta:
        ordering = ['-creation_date']
        get_latest_by = 'creation_date'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('massmedia_detail', (), {
            'mediatype': self.__class__.__name__.lower(),
            'slug': self.slug
        })

    def save(self, *args, **kwargs):
        if self.site_id is None:
            self.site = Site.objects.get_current()
        if self.external_url:
            self.process_external_url()
        super(Collection, self).save(*args, **kwargs)
        self.process_zipfile()
        super(Collection, self).save(*(), **{})

    def process_external_url(self):
        """
        Handle an external reference
        """
        # Get host for proper handling
        # Route to proper handler
        from urlparse import urlparse
        from youtube import YouTubeFeed
        url_struct = urlparse(self.external_url)
        if 'youtube' not in url_struct.hostname:
            return
        feed = YouTubeFeed(self.external_url)
        if feed:
            if not self.title:
                self.title = feed.metadata['title']
            self.slug = slugify(self.title)
            if not self.caption:
                self.caption = feed.metadata['subtitle']

    def process_zipfile(self):
        """
        Loop through a passed Zip file, saving the images and adding them to
        the Collection.
        """
        if not self.zip_file:
            return
        if not os.path.isfile(self.zip_file.path):
            return

        zip_file = zipfile.ZipFile(self.zip_file.path)
        bad_file = zip_file.testzip()
        if bad_file is not None:
            raise Exception(
                _('"%s" in the .zip archive is corrupt.') % bad_file
            )

        for filename in zip_file.namelist():
            if settings.DEBUG:
                print "Processing ", filename
            if filename.startswith('__') or filename.startswith('.'):
                # do not process hidden or meta files
                continue

            data = zip_file.read(filename)
            if len(data) == 0:
                continue

            title, extension = os.path.splitext(os.path.basename(filename))
            slug = slugify(title)

            try:
                model = EXT_TO_MODEL_MAP[extension[1:].lower()]
            except KeyError:
                continue

            if isinstance(model, Image):
                try:
                    trial_image = PilImage.open(StringIO(data))
                    trial_image.load()
                    trial_image = PilImage.open(StringIO(data))
                    trial_image.verify()
                except Exception, e:
                    if settings.DEBUG:
                        raise e
                    continue

            try:
                media = model.objects.get(slug=slug)
            except model.DoesNotExist:
                media = model(title=title, slug=slug)
                media.file.save(filename, ContentFile(data))

            CollectionRelation(content_object=media, collection=self).save()

        zip_file.close()
        os.remove(self.zip_file.path)
        try:
            self.zip_file.delete()
        except ValueError:
            pass

COLLECTION_LIMITS = {
    'model__in': ('image', 'audio', 'video', 'document', 'flash', )
}


class CollectionRelation(models.Model):
    """
    Generic Many-to-Many Relationships between a Collection and any other obj
    """
    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(
        ContentType,
        limit_choices_to=COLLECTION_LIMITS)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    position = models.PositiveSmallIntegerField(
        _("Position"),
        default=0,
        blank=True, null=True,
        editable=True)

    class Meta:
        ordering = ['position', 'id']

    def __unicode__(self):
        return unicode(self.content_object)


class MediaTemplate(models.Model):
    """
    Templates to display media, stored in the database
    """
    name = models.CharField(
        _("Name"),
        max_length=255,
        choices=((_('detail'), _('detail')), (_('thumb'), _('thumb'))))
    mimetype = models.CharField(
        _("MIME Type"),
        max_length=255,
        null=True, blank=True)
    content = models.TextField(_("Content"))

    def __unicode__(self):
        return "%s_%s template" % (self.mimetype, self.name)

    def template(self):
        """
        Return a Django Template object from the content of the record
        """
        return Template(self.content)
