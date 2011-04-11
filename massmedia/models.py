import sys
from time import strftime
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
from django.utils.translation import ugettext as _

from massmedia import settings as appsettings
from fields import Metadata, SerializedObjectField, MetadataJSONEncoder, MetadataJSONDecoder

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO
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

if 'tagging' in settings.INSTALLED_APPS:
    from tagging.fields import TagField
    HAS_TAGGING = True
else:
    HAS_TAGGING = False
        
try:
    import Image as PilImage
except ImportError:
    from PIL import Image as PilImage

out,err = sys.stdout,sys.stderr

try:
    from hachoir_core.error import HachoirError
    from hachoir_core.stream import InputStreamError
    from hachoir_parser import createParser
    from hachoir_metadata import extractMetadata
    extract_metadata = True
except ImportError:
    extract_metadata = False

sys.stdout,sys.stderr = out,err

IMAGE_STORAGE = get_storage_class(appsettings.IMAGE_STORAGE)
VIDEO_STORAGE = get_storage_class(appsettings.VIDEO_STORAGE)
AUDIO_STORAGE = get_storage_class(appsettings.AUDIO_STORAGE)
FLASH_STORAGE = get_storage_class(appsettings.FLASH_STORAGE)
DOC_STORAGE  = get_storage_class(appsettings.DOC_STORAGE)

is_image = lambda s: os.path.splitext(s)[1][1:] in appsettings.IMAGE_EXTS
value_or_list = lambda x: len(x) == 1 and x[0] or x

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

def custom_upload_to(prefix_path):
    """ Clean the initial file name and build a destination path based on settings as prefix_path"""
    def upload_callback(instance, filename):
        #-- Split and clean the filename with slugify
        filename = os.path.basename(filename)
        name, dot, extension = filename.rpartition('.')
        slug = slugify(name)
        clean_filename = '%s.%s' % (slug, extension.lower())
        #-- Build a destination path with previous cleaned string.
        destination_path = os.path.join(strftime(prefix_path), clean_filename)

        return destination_path

    return upload_callback

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
    if HAS_TAGGING:
        categories = TagField(blank=True,null=True)
    reproduction_allowed = models.BooleanField(_("we have reproduction rights for this media"), default=True)
    public = models.BooleanField(help_text=_("this media is publicly available"), default=True)
    external_url = models.URLField(blank=True,null=True,help_text=_("If this URLField is set, the media will be pulled externally"))
    mime_type = models.CharField(max_length=150,blank=True,null=True)
    width = models.IntegerField(blank=True, null=True, help_text=_("The width of the widget for the media"))
    height = models.IntegerField(blank=True, null=True, help_text=_("The height of the widget for the media"))
    
    widget_template = models.CharField(max_length=255,blank=True,null=True,
                help_text=_("The template name used to generate the widget (defaults to mime_type layout)"))
    
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
        if self.external_url and not self.mime_type:
            self.mime_type, blank = mimetypes.guess_type(self.external_url)
        if not self.metadata and hasattr(self,'file') and self.file and extract_metadata:
            self.parse_metadata()
        self.thumb()
        super(Media, self).save(*args, **kwargs)
    
    def thumb(self):
        return "<p>" + _("No Thumbnail Available") + "</p>"
    thumb.allow_tags = True
    thumb.short_description = _("Thumbnail")
    
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
                    return get_template('massmedia/mediatypes/generic_%s.html' % template_type)
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
                    raise TemplateDoesNotExist(_("Can't find a template to render the media. Looking in %s") % ", ".join(lookups))
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
    render_thumb.allow_tags=True
    
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
        
        for key, val in data.items():
            if isinstance(val, basestring):
                data[key] = super_force_ascii(val)
        
        self.metadata = Metadata(data)

class Image(Media):
    """
    We are using a File field instead of Image field because the Image field will 
    cause a problem if the file doesn't exist and you merely access the record.
    """
    file = models.FileField( #ImageField(
        upload_to =  custom_upload_to(appsettings.IMAGE_UPLOAD_TO),
        blank = True, 
        null = True,
        #width_field='width',
        #height_field='height',
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
    original = models.ForeignKey('self', related_name="variations", blank=True, null=True)
    
    def save(self, *args, **kwargs):
        generate_thumb = self.id is None
        super(Image, self).save(*args, **kwargs)
        if generate_thumb:
            self._generate_thumbnail()
        
    def _generate_thumbnail(self):
        from django.core.files.base import ContentFile
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

        if width==20000 and height==20000:
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
    
    def parse_metadata(self):
        super(Image, self).parse_metadata()
        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']
        self.one_off_author = self.metadata['Author'] or self.metadata['80'] or ''
        if not self.caption:
            self.caption = self.metadata['120'] or ''
        tags = []
        tags.extend(self.metadata["15"] or [])
        tags.extend(self.metadata["20"] or [])
        tags.extend(self.metadata["25"] or [])
        categories = ", ".join([x[:50] for x in tags])
        self.categories = super_force_ascii(categories)

class Embed(Media):
    code = models.TextField(help_text=_("Embed HTML source code"),blank=True,null=True)

    @property
    def media_url(self):
        return self.external_url 

class Video(Media):
    file = models.FileField(
        upload_to = custom_upload_to(appsettings.VIDEO_UPLOAD_TO),
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
    thumb.short_description = _("Thumbnail")    
    @property
    def media_url(self):
        return self.external_url or self.file.url
    
    def parse_metadata(self):
        super(Video, self).parse_metadata()
        self.width = self.metadata['Image width']
        self.height = self.metadata['Image height']


class GrabVideo(Video):
    asset_id = models.CharField(max_length=255,help_text=_("Grab video asset ID (the `a` parameter)"))
    layout_id = models.CharField(max_length=255,help_text=_("Grab video asset ID (the `m` parameter)"))
    
    if HAS_TAGGING:
        keywords = TagField(null=True,blank=True)
    
    def save(self, *a, **kw):
        if self.asset_id and len(self.asset_id) and not self.asset_id[0] in 'PV':
            self.asset_id = 'V%s' % self.asset_id
        super(GrabVideo, self).save(*a, **kw)


class Audio(Media):
    file = models.FileField(
        upload_to = custom_upload_to(appsettings.AUDIO_UPLOAD_TO),
        blank = True, 
        null = True,
        storage=AUDIO_STORAGE())
    
    class Meta:
        verbose_name=_("audio clip")
        verbose_name_plural=_("audio clips")
    
    @property
    def media_url(self):
        return self.external_url or self.file.url

class Flash(Media):
    file = models.FileField(
        upload_to = custom_upload_to(appsettings.FLASH_UPLOAD_TO),
        blank = True, 
        null = True,
        storage=FLASH_STORAGE())
    
    
    class Meta:
        verbose_name=_("SWF File")
        verbose_name_plural=_("SWF Files")
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
    
class Document(Media):
    file = models.FileField(
        upload_to = custom_upload_to(appsettings.DOC_UPLOAD_TO),
        blank = True, 
        null = True,
        storage=DOC_STORAGE())
    
    class Meta:
        verbose_name=_("Document")
        verbose_name_plural=_("Documents")
    
    @property
    def media_url(self):
        return self.external_url or self.file.url
   
class Collection(models.Model):
    creation_date = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    caption = models.TextField(blank=True)
    zip_file = models.FileField(_("Media files in a .zip"), upload_to='tmp', blank=True,null=True,
                        help_text=_("Select a .zip file of media to upload into a the Collection."))
    public = models.BooleanField(help_text=_("this collection is publicly available"), default=True)
    site = models.ForeignKey(Site)
    
    if HAS_TAGGING:
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
                raise Exception(_('"%s" in the .zip archive is corrupt.') % zip)
            for filename in zip.namelist():
                if filename.startswith('__') or filename.startswith('.'):
                    # do not process hidden or meta files
                    continue
                data = zip.read(filename)
                size = len(data)
                if size:
                    title,ext = os.path.splitext(os.path.basename(filename))
                    ext = ext[1:].lower()
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
                        continue
                        #raise TypeError, 'Unknown media extension %s'%ext
                    try:
                        media = model.objects.get(slug=slug) #XXX
                    except model.DoesNotExist:
                        media = model(title=title, slug=slug)
                        media.file.save(filename, ContentFile(data))                      
                        # XXX: Make site relations possible, send signals
                        CollectionRelation(content_object=media,collection=self).save()
            zip.close()
            os.remove(self.zip_file.path)
            try:
                self.zip_file.delete()
            except ValueError:
                pass
            super(Collection, self).save(*(), **{})

collection_limits = {'model__in':('image','audio','video','document','flash')}
class CollectionRelation(models.Model):
    collection = models.ForeignKey(Collection)
    content_type = models.ForeignKey(ContentType, limit_choices_to=collection_limits)
    object_id = models.PositiveIntegerField()
    content_object = generic.GenericForeignKey('content_type', 'object_id')
    position = models.PositiveSmallIntegerField(_("Position"), default = 0, blank = True, null=True, editable=True)
    
    class Meta:
        ordering = ['position', 'id']
    
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
        
        

