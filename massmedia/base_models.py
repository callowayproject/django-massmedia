import sys
import mimetypes

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.utils.translation import ugettext as _
from django.contrib.sites.managers import CurrentSiteManager
from django.template.loader import select_template
from django.template import Context, TemplateDoesNotExist

from fields import (Metadata, SerializedObjectField,
                    MetadataJSONEncoder, MetadataJSONDecoder)

from massmedia import settings as appsettings
from massmedia.utils import value_or_list, super_force_ascii

# Patch mimetypes w/ any extra types
mimetypes.types_map.update(appsettings.EXTRA_MIME_TYPES)

# This is required because the Hachoir package screws up the stdout and stderr
OUT, ERR = sys.stdout, sys.stderr
try:
    from hachoir_core.error import HachoirError
    from hachoir_core.stream import InputStreamError
    from hachoir_parser import createParser
    from hachoir_metadata import extractMetadata
    EXTRACT_METADATA = True
except ImportError:
    EXTRACT_METADATA = False
sys.stdout, sys.stderr = OUT, ERR


class PublicMediaManager(CurrentSiteManager):
    def __init__(self):
        super(PublicMediaManager, self).__init__('site')

    def public(self):
        return self.get_queryset().filter(public=True)


class Media(models.Model):
    """
    The abstract base class for all media types. It includes all the common
    attributes and functions.
    """
    title = models.CharField(
        _("Title"),
        max_length=255)
    slug = models.SlugField(
        _("Slug"),
        unique=True)
    creation_date = models.DateTimeField(
        _("Creation Date"),
        auto_now_add=True)
    author = models.ForeignKey(
        User,
        blank=True, null=True,
        limit_choices_to={'is_staff': True})
    one_off_author = models.CharField(
        _('One-off Author'),
        max_length=100,
        blank=True)
    caption = models.TextField(
        _("Caption"),
        blank=True)
    metadata = SerializedObjectField(
        _("Metadata"),
        blank=True,
        encoder=MetadataJSONEncoder,
        decoder=MetadataJSONDecoder)
    site = models.ForeignKey(
        Site,
        related_name='%(class)s_site')
    reproduction_allowed = models.BooleanField(
        _("we have reproduction rights for this media"),
        default=True)
    public = models.BooleanField(
        _("Public"),
        help_text=_("this media is publicly available"),
        default=True)
    external_url = models.URLField(
        _("External URL"),
        blank=True, null=True,
        help_text=_("If this URL Field is set, the media will be pulled externally"))
    mime_type = models.CharField(
        _("MIME type"),
        max_length=150,
        blank=True, null=True)
    width = models.IntegerField(
        _("Width"),
        blank=True, null=True,
        help_text=_("The width of the widget for the media"))
    height = models.IntegerField(
        _("Height"),
        blank=True, null=True,
        help_text=_("The height of the widget for the media"))

    widget_template = models.CharField(
        _("Widget Template"),
        max_length=255,
        blank=True, null=True,
        help_text=_("The template name used to generate the widget (defaults to MIME type layout)"))

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
        return ('massmedia_detail', (), {
            'mediatype': self.__class__.__name__.lower(),
            'slug': self.slug
        })

    @property
    def media_url(self):
        return self.external_url

    def save(self, *args, **kwargs):
        if self.site_id is None:
            self.site = Site.objects.get_current()
        super(Media, self).save(*args, **kwargs)

        # That save needs to come before we look at the file otherwise the
        # self.file.path is incorrect.
        if hasattr(self, 'file') and self.file and not self.mime_type:
            self.mime_type = mimetypes.guess_type(self.file.path)[0]

        if self.external_url and not self.mime_type:
            self.mime_type, blank = mimetypes.guess_type(self.external_url)

        if not self.metadata and hasattr(self, 'file') and self.file and EXTRACT_METADATA:
            self.parse_metadata()
        try:
            super(Media, self).save(*args, **kwargs)
        except Exception, e:
            print e
            print self.__dict__

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

    def get_template(self, template_type="detail"):
        mime_type = self.get_mime_type()
        if appsettings.FS_TEMPLATES:
            if self.widget_template:
                lookups = [self.widget_template]
            elif mime_type is None:
                lookups = [
                    'massmedia/mediatypes/generic_%s.html' % template_type
                ]
            else:
                lookups = [
                    'massmedia/mediatypes/%s_%s.html' % (mime_type, template_type),
                    'massmedia/mediatypes/%s/generic_%s.html' % (mime_type.split('/')[0], template_type),
                    'massmedia/mediatypes/generic_%s.html' % template_type
                ]
            try:
                return select_template(lookups)
            except TemplateDoesNotExist:
                raise TemplateDoesNotExist(_("Can't find a template to render the media. Looking in %s") % ", ".join(lookups))
        else:
            from massmedia.models import MediaTemplate
            if self.widget_template:
                lookups = [{'name': self.widget_template}]
            elif mime_type is None:
                lookups = [{'mimetype': ''}]
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

    def _render(self, template_type):
        tmpl = self.get_template(template_type)
        ctxt = Context({
            'media': self,
            'MEDIA_URL': settings.MEDIA_URL,
            'STATIC_URL': getattr(settings, 'STATIC_URL', settings.MEDIA_URL)
        })
        return tmpl.render(ctxt)

    def render_thumb(self):
        return self._render('thumb')
    render_thumb.allow_tags = True

    def render_detail(self):
        return self._render('detail')

    def _get_raw_metadata(self, path):
        """
        Return the raw metadata as a dictionary
        """
        try:
            parser = createParser(unicode(path))
            if not parser:
                if settings.DEBUG:
                    raise Exception("No parser was created.")
                return {}
            metadata = extractMetadata(parser, appsettings.INFO_QUALITY)
            if not metadata:
                # if settings.DEBUG:
                #     raise Exception("No metadata was extracted.")
                return {}
        except (InputStreamError, HachoirError):
            if settings.DEBUG:
                raise
            return {}
        return dict([(x.description, value_or_list([item.value for item in x.values])) for x in sorted(metadata) if x.values])

    def parse_metadata(self):
        data = self._get_raw_metadata(self.file.path)

        for key, val in data.items():
            if isinstance(val, basestring):
                data[key] = super_force_ascii(val)

        self.metadata = Metadata(data)
