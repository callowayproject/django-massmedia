from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes import generic
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify
from django.conf import settings
from django.core.files.base import ContentFile
from django.template.loader import get_template
from django.template import TemplateDoesNotExist,Template,Context
from django.core.exceptions import ImproperlyConfigured

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
    try:
        from PIL import Image as PilImage
    except ImportError:
        PilImage = 0

try:
    from hachoir_core.error import HachoirError
    from hachoir_core.stream import InputStreamError
    from hachoir_parser import createParser
    from hachoir_metadata import extractMetadata
except ImportError:
    extractMetadata = None


is_image = lambda s: os.path.splitext(s)[1][1:] in appsettings.IMAGE_EXTS
value_or_list = lambda x: len(x) == 1 and x[0] or x

class Media(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    creation_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(User, blank=True, null=True, limit_choices_to={'is_staff':True})
    one_off_author = models.CharField('one-off author', max_length=100, blank=True)
    credit = models.CharField(max_length=150, blank=True)
    caption = models.TextField(blank=True)
    metadata = SerializedObjectField(blank=True, encoder=MetadataJSONEncoder, decoder=MetadataJSONDecoder)
    sites = models.ManyToManyField(Site,related_name='%(class)s_sites')
    categories = TagField(blank=True,null=True)
    reproduction_allowed = models.BooleanField("we have reproduction rights for this media", default=True)
    public = models.BooleanField(help_text="this media is publicly available", default=True)
    external_url = models.URLField(blank=True,null=True,help_text="If this URLField is set, the media will be pulled externally")
    mime_type = models.CharField(max_length=150,blank=True,null=True)
    width = models.IntegerField(blank=True, null=True, help_text="The width of the widget for the media")
    height = models.IntegerField(blank=True, null=True, help_text="The height of the widget for the media")
    
    widget_template = models.CharField(max_length=255,blank=True,null=True,
                help_text='The template name used to generate the widget (defaults to mime_type layout)')

    class Meta:
        ordering = ('-creation_date',)
        abstract = True
        
    def __unicode__(self):
        return self.title
    
    def author_name(self):
        if self.author:
            return self.author.full_name
        else:
            return self.one_off_author
    
    def get_absolute_url(self):
        if self.external_url:
            return self.external_url
        if hasattr(self,'file') and getattr(self,'file',None):
            return self.absolute_url((
                settings.MEDIA_URL,
                self.creation_date.strftime("%Y/%b/%d"),
                os.path.basename(self.file.path)))
        return ''
        
    def absolute_url(self, format):
        raise NotImplementedError
    
    def save(self, *args, **kwargs):
        super(Media, self).save(*args, **kwargs) 
        # That save needs to come before we look at the file otherwise the
        # self.file.path is incorrect.
        if self.file and not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]
        if not(self.metadata) and self.file and extractMetadata:
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
        return
    
    def get_template(self):
        mime_type = self.get_mime_type()
        if self.widget_template:
            if appsettings.TEMPLATE_MODE == 1:
                return get_template(self.widget_template)
            else:
                return MediaTemplate.objects.get(name=self.widget_template).template()
        elif mime_type is None:
            if appsettings.TEMPLATE_MODE == 1:
                if isinstance(self, GrabVideo):
                    return get_template('massmedia/grab.html')
                else:
                    return get_template('massmedia/generic.html')
            else:
                return MediaTemplate.objects.get(mimetype='').tempate()
        else:
            if appsettings.TEMPLATE_MODE == 1:
                try:
                    return get_template('massmedia/%s.html'%mime_type)
                except TemplateDoesNotExist:
                    try:
                        return get_template('massmedia/%s/generic.html'%mime_type.split('/')[0])
                    except TemplateDoesNotExist:
                        return get_template('massmedia/generic.html')
            else:
                try:
                    return MediaTemplate.objects.get(mimetype=mime_type)
                except MediaTemplate.DoesNotExist:
                    try:
                        return MediaTemplate.objects.get(mimetype=mime_type.split('/')[0])
                    except MediaTemplate.DoesNotExist:
                        return MediaTemplate.objects.get(mimetype='').tempate()
       
    def render_template(self): 
        return self.get_template().render(Context({
            'media':self,
            'MEDIA_URL':settings.MEDIA_URL
        }))
    
    def parse_metadata(self):
        path = self.file.path
        
        try:
            parser = createParser(unicode(path))
            if not parser:
                return
            metadata = extractMetadata(parser, appsettings.INFO_QUALITY)
            if not metadata:
                return
        except InputStreamError, HachoirError:
            return
        data = dict([(x.description, value_or_list([item.value for item in x.values])) for x in sorted(metadata) if x.values])
        
        if is_image(path) and iptc:
            try:
                data.update(IPTCInfo(path).__dict__['_data'])
            except:
                pass
        self.metadata = Metadata(data)

class Image(Media):
    file = models.ImageField(upload_to='img/%Y/%b/%d', blank=True, null=True)
    
    def thumb(self):
        if self.file:
            thumbnail = '%s.thumb%s'%os.path.splitext(self.file.path)
            thumburl = thumbnail[len(os.path.abspath(settings.MEDIA_ROOT)):]
            if not os.path.exists(thumbnail):
                try:
                    im = PilImage.open(self.file)
                except:
                    return ''
                im.thumbnail(appsettings.THUMB_SIZE,PilImage.ANTIALIAS)
                im.save(thumbnail,im.format)
            return '<a href="%s"><img src="%s%s"/></a>'%\
                        (self.get_absolute_url(),settings.MEDIA_URL,thumburl)
        elif self.external_url:
            return '<a href="%s"><img src="%s"/></a>'%\
                        (self.get_absolute_url(),self.get_absolute_url())
        return ''
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    def thumb_no_link(self):
        self.thumb()
        if self.file:
            thumbnail = '%s.thumb%s'%os.path.splitext(self.file.path)
            thumburl = thumbnail[len(os.path.abspath(settings.MEDIA_ROOT)):]
            return '<img src="%s%s"/>' % (settings.MEDIA_URL, thumburl)
        elif self.external_url:
            return '<img src="%s"/>' % self.get_absolute_url()
        return ''
    
    def absolute_url(self, format):
        return "%simg/%s/%s" % format
    
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

class Video(Media):
    file = models.FileField(upload_to='video/%Y/%b/%d', blank=True, null=True)
    thumbnail = models.ForeignKey(Image, null=True, blank=True)
    
    def thumb(self):
        return self.thumbnail.thumb()
    thumb.allow_tags = True
    thumb.short_description = 'Thumbnail'
    
    def absolute_url(self, format):
        return "%svideo/%s/%s" % format

class GrabVideo(Video):
    asset_id = models.CharField(max_length=255,help_text='Grab video asset ID (the `a` parameter)')
    layout_id = models.CharField(max_length=255,help_text='Grab video asset ID (the `m` parameter)')
    
    keywords = TagField(null=True,blank=True)
    
    def save(self, *a, **kw):
        if self.asset_id and len(self.asset_id) and not self.asset_id[0] in 'PV':
            self.asset_id = 'V%s' % self.asset_id
        super(GrabVideo, self).save(*a, **kw)
    
    def absolute_url(self, format):
        return "%sgrabvideo/%s/%s" % format
    
class Audio(Media):
    file = models.FileField(upload_to='audio/%Y/%b/%d', blank=True, null=True)
    def absolute_url(self, format):
        return "%saudio/%s/%s" % format

class Flash(Media):
    file = models.FileField(upload_to='flash/%Y/%b/%d', blank=True, null=True)
    def absolute_url(self, format):
        return "%sflash/%s/%s" % format
    
class Document(Media):
    file = models.FileField(upload_to='docs/%Y/%b/%d', blank=True, null=True)
    def absolute_url(self, format):
        return "%sdocs/%s/%s" % format
   
class Collection(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255, unique=True)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    zip_file = models.FileField('Media files in a .zip', upload_to='tmp', blank=True,null=True,
                        help_text='Select a .zip file of media to upload into a the Collection.')
    public = models.BooleanField(help_text="this collection is publicly available", default=True)
    sites = models.ManyToManyField(Site)
    categories = TagField(null=True,blank=True)
    
    class Meta:
        ordering = ['-creation_date']
        get_latest_by = 'creation_date'

    def __unicode__(self):
        return self.title
 
    def save(self, *args, **kwargs):
        super(Collection, self).save(*args, **kwargs)
        self.process_zipfile()
        
    def process_zipfile(self):
        if self.zip_file and os.path.isfile(self.zip_file.path):
            zip = zipfile.ZipFile(self.zip_file.path)
            if zip.testzip():
                raise Exception('"%s" in the .zip archive is corrupt.' % bad_file)
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
                        media.sites.add(Site.objects.get_current())
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
    name = models.CharField(max_length=255)
    mimetype = models.CharField(max_length=255,null=True,blank=True)
    content = models.TextField()
    
    def __unicode__(self):
        return self.name
    
    def template(self):
        return Template(self.content)

# Ellington Extras
if 'ellington.news' in settings.INSTALLED_APPS:
    from ellington.news.parts.inlines import register_inline,ObjectInline
    
    register_inline('massmedia-grabvideo', ObjectInline('massmedia-grabvideo','MassMedia -- Grab Videos','massmedia','grabvideo','grabvideo'))
    register_inline('massmedia-video', ObjectInline('massmedia-video','MassMedia -- Videos','massmedia','video','video'))
    register_inline('massmedia-audio', ObjectInline('massmedia-audio','MassMedia -- Audios','massmedia','audio','audio'))
    register_inline('massmedia-image', ObjectInline('massmedia-image','MassMedia -- Images','massmedia','image','image'))
    register_inline('massmedia-flash', ObjectInline('massmedia-flash','MassMedia -- Flashes','massmedia','flash','flash'))
    register_inline('massmedia-document', ObjectInline('massmedia-document','MassMedia -- Documents','massmedia','document','document'))
