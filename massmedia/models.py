from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import get_storage_class
from django.template.loader import get_template, select_template
from django.template import Template, Context, TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured
from sorl.thumbnail.fields import ImageWithThumbnailsField

from massmedia import settings as appsettings
from fields import Metadata, SerializedObjectField, MetadataJSONEncoder, MetadataJSONDecoder

from cStringIO import StringIO
import mimetypes
import os
import zipfile

# Patch mimetypes w/ any extra types
mimetypes.types_map.update(appsettings.EXTRA_MIME_TYPES)

try:
    from iptcinfo import IPTCInfo
    iptc = 1
except ImportError:
    iptc = 0

try:
    from tagging.fields import TagField
except ImportError:
    raise ImproperlyConfigured('You must have django-tagging installed!')
        
try:
    import Image as PilImage
except ImportError:
    from PIL import Image as PilImage


try:
    from hachoir_core.error import HachoirError
    from hachoir_core.stream import InputStreamError
    from hachoir_parser import createParser
    from hachoir_metadata import extractMetadata
    extract_metadata = True
except ImportError:
    extract_metadata = False


IMAGE_STORAGE = get_storage_class(appsettings.IMAGE_STORAGE)
VIDEO_STORAGE = get_storage_class(appsettings.VIDEO_STORAGE)
AUDIO_STORAGE = get_storage_class(appsettings.AUDIO_STORAGE)
FLASH_STORAGE = get_storage_class(appsettings.FLASH_STORAGE)
DOC_STORAGE  = get_storage_class(appsettings.DOC_STORAGE)

is_image = lambda s: os.path.splitext(s)[1][1:] in appsettings.IMAGE_EXTS
value_or_list = lambda x: len(x) == 1 and x[0] or x

class PublicMediaManager(CurrentSiteManager):
    def __init__(self):
        super(PublicMediaManager, self).__init__('site')
    
    def public(self):
        return self.get_query_set().filter(public=True)

class Media(models.Model):
    """
    The abstract base class for all media types. It includes all the common 
    attributes and functions.
    """
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'is_staff':True})
    one_off_author = models.CharField('one-off author', max_length=100, blank=True)
    caption = models.TextField(blank=True)
    metadata = SerializedObjectField(blank=True, encoder=MetadataJSONEncoder, decoder=MetadataJSONDecoder)
    site = models.ForeignKey(Site, related_name='%(class)s_site')
    categories = TagField(blank=True,null=True)
    reproduction_allowed = models.BooleanField("we have reproduction rights for this media", default=True)
    public = models.BooleanField(help_text="this media is publicly available", default=True)
    external_url = models.URLField(blank=True,null=True,help_text="If this URLField is set, the media will be pulled externally")
    mime_type = models.CharField(max_length=150,blank=True,null=True)
    width = models.IntegerField(blank=True, null=True, help_text="The width of the widget for the media")
    height = models.IntegerField(blank=True, null=True, help_text="The height of the widget for the media")
    
    widget_template = models.CharField(max_length=255,blank=True,null=True,
                help_text='The template name used to generate the widget (defaults to mime_type layout)')
    
    objects = PublicMediaManager()
    
    class Meta:
        ordering = ('-creation_date',)
        abstract = True
        
    def __unicode__(self):
        return self.title
    
    @property
    def author_name(self):
        if self.author:
            return self.author.full_name
        else:
            return self.one_off_author
    
    @models.permalink
    def get_absolute_url(self):
        return ('massmedia_detail', (),{'mediatype': self.__class__.__name__.lower(), 'slug': self.slug})
    
    @property
    def media_url(self):
        return self.external_url
    
    def save(self, *args, **kwargs):
        if self.site_id is None:
            self.site = Site.objects.get_current()
        super(Media, self).save(*args, **kwargs) 
        # That save needs to come before we look at the file otherwise the
        # self.file.path is incorrect.
        if hasattr(self,'file') and self.file and not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]
        if not self.metadata and hasattr(self,'file') and self.file and extract_metadata:
            self.parse_metadata()
        self.thumb()
        super(Media, self).save(*args, **kwargs)
    
    def thumb(self):
        return '<p>No Thumbnail Available</p>'
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    def get_mime_type(self):
        if self.mime_type:
            return self.mime_type
        if self.metadata and 'mime_type' in self.metadata:
            return self.metadata['mime_type']
        return None
    
    def get_template(self, template_type):
        mime_type = self.get_mime_type()
        if isinstance(self, Embed):
            return get_template('massmedia/embed.html')   
        elif self.widget_template:
            if appsettings.FS_TEMPLATES:
                return get_template(self.widget_template)
            else:
                return MediaTemplate.objects.get(name=self.widget_template).template()
        elif mime_type is None:
            if appsettings.FS_TEMPLATES:
                if isinstance(self, GrabVideo):
                    return get_template('massmedia/grab.html')
                else:
                    return get_template('massmedia/generic.html')
            else:
                return MediaTemplate.objects.get(mimetype='').tempate()
        else:
            if appsettings.FS_TEMPLATES:
                lookups = [
                    'massmedia/mediatypes/%s_%s.html' % (mime_type, template_type),
                    'massmedia/mediatypes/%s/generic_%s.html' % (mime_type.split('/')[0], template_type),
                    'massmedia/mediatypes/generic_%s.html' % template_type
                ]
                try:
                    return select_template(lookups)
                except TemplateDoesNotExist, e:
                    raise TemplateDoesNotExist("Can't find a template to render the media. Looking in %s" % ", ".join(lookup))
            else:
                lookups = [
                    dict(mimetype=mime_type, name=template_type),
                    dict(mimetype=mime_type.split('/')[0], name=template_type),
                    dict(mimetype='', name=template_type)
                ]
                for kwargs in lookups:
                    try:
                        return MediaTemplate.objects.get(**kwargs)
                    except MediaTemplate.DoesNotExist:
                        pass
                return MediaTemplate.objects.get(mimetype='').template()
    
    def _render(self, format):
        t = self.get_template(format)
        c = Context({
            'media':self,
            'MEDIA_URL':settings.MEDIA_URL,
            'STATIC_URL': getattr(settings, 'STATIC_URL', settings.MEDIA_URL)
        })
        return t.render(c)
    
    def render_thumb(self):
        return self._render('thumb')
    
    def render_detail(self):
        return self._render('detail')
    
    def parse_metadata(self):
        path = self.file.path
        
        try:
            parser = createParser(unicode(path))
            if not parser:
                return
            metadata = extractMetadata(parser, appsettings.INFO_QUALITY)
            if not metadata:
                return
        except (InputStreamError, HachoirError):
            return
        data = dict([(x.description, value_or_list([item.value for item in x.values])) for x in sorted(metadata) if x.values])
        
        if is_image(path) and iptc:
            try:
                data.update(IPTCInfo(path).__dict__['_data'])
            except:
                pass
        self.metadata = Metadata(data)

class Image(Media):
    file = ImageWithThumbnailsField(
        upload_to = appsettings.IMAGE_UPLOAD_TO,
        blank = True, 
        null = True,
        thumbnail = appsettings.THUMBNAIL_OPTS,
        extra_thumbnails = appsettings.EXTRA_THUMBS,
        storage=IMAGE_STORAGE(),
        generate_on_save=True)
    original = models.ForeignKey('self', related_name="variations", blank=True, null=True)
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
    
    def parse_metadata(self):
        super(Image, self).parse_metadata()
        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']
        self.one_off_author = self.metadata['Author'] or self.metadata['80'] or ''
        self.caption = self.metadata['120'] or ''
        tags = []
        tags.extend(self.metadata["15"] or [])
        tags.extend(self.metadata["20"] or [])
        tags.extend(self.metadata["25"] or [])
        self.categories = ", ".join(tags)

class Embed(Media):
    code = models.TextField(help_text='Embed HTML source code')

    @property
    def media_url(self):
        return self.external_url 

class Video(Media):
    file = models.FileField(
        upload_to = appsettings.VIDEO_UPLOAD_TO,
        blank = True, 
        null = True,
        storage=VIDEO_STORAGE())
    thumbnail = models.ForeignKey(Image, null=True, blank=True)
    
    def thumb(self):
        if self.thumbnail:
            return self.thumbnail.thumb()
        else:
            return ''
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
    
    def parse_metadata(self):
        super(Video, self).parse_metadata()
        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']


class GrabVideo(Video):
    asset_id = models.CharField(max_length=255,help_text='Grab video asset ID (the `a` parameter)')
    layout_id = models.CharField(max_length=255,help_text='Grab video asset ID (the `m` parameter)')
    
    keywords = TagField(null=True,blank=True)
    
    def save(self, *a, **kw):
        if self.asset_id and len(self.asset_id) and not self.asset_id[0] in 'PV':
            self.asset_id = 'V%s' % self.asset_id
        super(GrabVideo, self).save(*a, **kw)


class Audio(Media):
    file = models.FileField(
        upload_to = appsettings.AUDIO_UPLOAD_TO,
        blank = True, 
        null = True,
        storage=AUDIO_STORAGE())
    
    class Meta:
        verbose_name="audio clip"
        verbose_name_plural="audio clips"
    
    @property
    def media_url(self):
        return self.external_url or self.file.url

class Flash(Media):
    file = models.FileField(
        upload_to = appsettings.FLASH_UPLOAD_TO,
        blank = True, 
        null = True,
        storage=FLASH_STORAGE())
    
    
    class Meta:
        verbose_name="SWF File"
        verbose_name_plural="SWF Files"
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
    
class Document(Media):
    file = models.FileField(
        upload_to = appsettings.DOC_UPLOAD_TO,
        blank = True, 
        null = True,
        storage=DOC_STORAGE())
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
   
class Collection(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    zip_file = models.FileField('Media files in a .zip', upload_to='tmp', blank=True,null=True,
                        help_text='Select a .zip file of media to upload into a the Collection.')
    public = models.BooleanField(help_text="this collection is publicly available", default=True)
    site = models.ForeignKey(Site)
    categories = TagField(null=True,blank=True)
    
    objects = PublicMediaManager()
    
    class Meta:
        ordering = ['-creation_date']
        get_latest_by = 'creation_date'

    def __unicode__(self):
        return self.title

    @models.permalink
    def get_absolute_url(self):
        return ('massmedia_detail', (),{'mediatype': self.__class__.__name__.lower(), 'slug': self.slug})

    def save(self, *args, **kwargs):
        super(Collection, self).save(*args, **kwargs)
        self.process_zipfile()
        
    def process_zipfile(self):
        if self.zip_file and os.path.isfile(self.zip_file.path):
            zip = zipfile.ZipFile(self.zip_file.path)
            if zip.testzip():
                raise Exception('"%s" in the .zip archive is corrupt.' % zip)
            for filename in zip.namelist():
                if filename.startswith('__'): # do not process meta files
                    continue
                data = zip.read(filename)
                size = len(data)
                if size:
                    title,ext = os.path.splitext(os.path.basename(filename))
                    ext = ext[1:]
                    slug = slugify(title)
                    if ext in appsettings.IMAGE_EXTS:
                        model = Image
                        try:
                            trial_image = PilImage.open(StringIO(data))
                            trial_image.load()
                            trial_image = PilImage.open(StringIO(data))
                            trial_image.verify()
                        except Exception:
                            continue
                    elif ext in appsettings.VIDEO_EXTS:
                        model = Video
                    elif ext in appsettings.AUDIO_EXTS:
                        model = Audio
                    elif ext in appsettings.FLASH_EXTS:
                        model = Flash
                    elif ext in appsettings.DOC_EXTS:
                        model = Document
                    else:
                        raise TypeError, 'Unknown media extension %s'%ext
                    try:
                        media = model.objects.get(slug=slug) #XXX
                    except model.DoesNotExist:
                        media = model(title=title, slug=slug)
                        media.file.save(filename, ContentFile(data))                      
                        # XXX: Make site relations possible, send signals
                        CollectionRelation(content_object=media,collection=self).save()
            zip.close()
            os.remove(self.zip_file.path)
            self.zip_file.delete()
            super(Collection, self).save(*(), **{})

collection_limits = {'model__in':('image','audio','video','flash')}
class CollectionRelation(models.Model):
    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType, limit_choices_to=collection_limits)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    
    def __unicode__(self):
        return unicode(self.content_object)
        
class MediaTemplate(models.Model):
    name = models.CharField(max_length=255, choices=(('detail', 'detail'),('thumb', 'thumb')))
    mimetype = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField()
    
    def __unicode__(self):
        return "%s_%s template" % (self.mimetype, self.name)
    
    def template(self):
        return Template(self.content)
