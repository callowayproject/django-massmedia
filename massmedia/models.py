import os, zipfile
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

from massmedia import settings as appsettings
from base_models import Media, PublicMediaManager
from massmedia.utils import custom_upload_to, super_force_ascii

try:
    from iptcinfo import IPTCInfo
    HAS_IPTC = True
except ImportError:
    HAS_IPTC = False

if appsettings.USE_TAGGING:
    from tagging.fields import TagField

try:
    import Image as PilImage
except ImportError:
    from PIL import Image as PilImage

IMAGE_STORAGE = get_storage_class(appsettings.IMAGE_STORAGE)
VIDEO_STORAGE = get_storage_class(appsettings.VIDEO_STORAGE)
AUDIO_STORAGE = get_storage_class(appsettings.AUDIO_STORAGE)
FLASH_STORAGE = get_storage_class(appsettings.FLASH_STORAGE)
DOC_STORAGE  = get_storage_class(appsettings.DOC_STORAGE)

class Image(Media):
    """
    We are using a File field instead of Image field because the Image field will 
    cause a problem if the file doesn't exist and you merely access the record.
    """
    file = models.FileField(
        upload_to =  custom_upload_to(appsettings.IMAGE_UPLOAD_TO),
        blank = True, 
        null = True,
        storage=IMAGE_STORAGE())
    thumbnail = models.ImageField(
        upload_to = custom_upload_to(appsettings.THUMB_UPLOAD_TO),
        blank = True,
        null = True,
        width_field = 'thumb_width',
        height_field = 'thumb_height',
        editable=False,
        storage = IMAGE_STORAGE())
    thumb_width = models.IntegerField(blank=True, null=True, editable=False)
    thumb_height = models.IntegerField(blank=True, null=True, editable=False)
    original = models.ForeignKey(
        'self', 
        related_name="variations", 
        blank=True, null=True)
    
    def save(self, *args, **kwargs):
        generate_thumb = self.id is None
        super(Image, self).save(*args, **kwargs)
        if generate_thumb:
            self._generate_thumbnail()
        
    def _generate_thumbnail(self):
        if self.file:
            image = PilImage.open(self.file.path)
            filename = os.path.basename(self.file.name)
        elif self.external_url:
            import urllib
            filepath, headers = urllib.urlretrieve(self.external_url)
            image = PilImage.open(filepath)
            filename = os.path.basename(filepath)
        if image.mode not in ('L', 'RGB'):
            image = image.convert('RGB')
        image.thumbnail(appsettings.THUMB_SIZE, PilImage.ANTIALIAS)
        
        destination = StringIO()
        image.save(destination, format='JPEG')
        destination.seek(0)
        
        self.thumbnail.save(filename, ContentFile(destination.read()))
    
    def smart_fit(self, width=20000, height=20000):
        """
        Given a width, height or both, it will return the width and height to 
        fit in the given area.
        """
        im_width = self.width
        im_height = self.height

        if width == 20000 and height == 20000:
            return im_width, im_height
        elif width is None:
            width = 20000
        elif height is None:
            height = 20000
        
        if width < height:
            scale = float(width)/float(im_width)
            height = int(round(scale * im_height))
        else:
            scale = float(height)/float(im_height)
            width = int(round(scale * im_width))
        
        return width, height
    
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
        categories = ", ".join([x[:50] for x in tags])
        self.categories = super_force_ascii(categories)

class Embed(Media):
    code = models.TextField(
        _("Embed Code"), 
        help_text=_("Embed HTML source code"),
        blank=True, null=True)
    
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
        upload_to = custom_upload_to(appsettings.VIDEO_UPLOAD_TO),
        blank = True, 
        null = True,
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
        upload_to=custom_upload_to(appsettings.AUDIO_UPLOAD_TO),
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
        upload_to=custom_upload_to(appsettings.FLASH_UPLOAD_TO),
        blank=True, null=True,
        storage=FLASH_STORAGE())
    
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
        upload_to = custom_upload_to(appsettings.DOC_UPLOAD_TO),
        blank = True, 
        null = True,
        storage=DOC_STORAGE())
    
    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")
    
    @property
    def media_url(self):
        return self.external_url or self.file.url


EXT_TO_MODEL_MAP = {}
for ext in appsettings.IMAGE_EXTS:
    EXT_TO_MODEL_MAP[ext] = Image

for ext in appsettings.VIDEO_EXTS:
    EXT_TO_MODEL_MAP[ext] = Video

for ext in appsettings.AUDIO_EXTS:
    EXT_TO_MODEL_MAP[ext] = Audio

for ext in appsettings.FLASH_EXTS:
    EXT_TO_MODEL_MAP[ext] = Flash

for ext in appsettings.DOC_EXTS:
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
        verify_exists=False,
        help_text=_("Pull content from an external source. Supported: YouTube"))
    public = models.BooleanField(
        help_text=_("this collection is publicly available"), 
        default=True)
    site = models.ForeignKey(Site)
    
    if appsettings.USE_TAGGING:
        categories = TagField(
            _("Categories"), 
            null=True, blank=True)
    
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
            self.external_url = feed.url
            if not self.title:
                self.title = feed.metadata['title']
            self.slug = slugify(self.title)
            if not self.caption:
                self.caption = feed.metadata['subtitle']
            #self.metadata = feed.metadata
    
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
            #if settings.DEBUG:
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
        choices=((_('detail'), _('detail')),(_('thumb'), _('thumb'))))
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

