from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget, AdminURLFieldWidget
from django.contrib.contenttypes.models import ContentType
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _


from models import (Image, Video, Audio, Flash, Collection, Embed, Document,
    CollectionRelation, MediaTemplate)
import settings
from forms import (ImageCreationForm, VideoCreationForm, AudioCreationForm,
    FlashCreationForm, DocumentCreationForm, EmbedCreationForm)

# from templatetags.media_widgets import snipshot_url


class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and hasattr(value, 'instance') and value.instance.thumbnail:
            thumbnail = value.instance.thumbnail.url
            width = value.instance.thumb_width
            height = value.instance.thumb_height
            # snipshot = snipshot_url(value.instance)
            # crop_tag = '''<br /><a class="link" href="#" onclick="var win = window.open('%s','snipshot', 'height=500,width=800,resizable=yes,scrollbars=yes');win.focus();">Crop image with snipshot</a>''' % snipshot
            tag = u'<img src="%s" width="%s" height="%s"/>' % (
                thumbnail, width, height)
        else:
            # crop_tag = u""
            tag = _("<strong>No Thumbnail available</strong>")
        if value:
            output.append(u'<a href="%s" target="_blank">%s</a>' % (
                value.url, tag))
            # output.append(crop_tag)
        return mark_safe(u''.join(output))


class AdminExternalURLWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        output = []
        tag = _("<strong>No Thumbnail available</strong>")
        if value:
            output.append(u'<a href="%s" target="_blank">%s</a>' % (value, tag))
            output.append(u'<br /><a href="%s" target="_blank">%s</a>' % (value, value))
        return mark_safe(u''.join(output))


class GenericCollectionInlineModelAdmin(admin.options.InlineModelAdmin):
    ct_field = 'content_type'
    ct_fk_field = 'object_id'
    fields = ('content_type', 'object_id', 'position')
    extra = 3

    def __init__(self, parent_model, admin_site):
        super(GenericCollectionInlineModelAdmin, self).__init__(parent_model, admin_site)
        ctypes = ContentType.objects.all().order_by('id').values_list('id', 'app_label', 'model')
        elements = ["%s: '%s/%s'" % (x, y, z) for x, y, z in ctypes]
        self.content_types = "{%s}" % ",".join(elements)

    def get_formset(self, request, obj=None):
        result = super(GenericCollectionInlineModelAdmin, self).get_formset(request, obj)
        result.content_types = self.content_types
        result.ct_fk_field = self.ct_fk_field
        return result


class GenericCollectionTabularInline(GenericCollectionInlineModelAdmin):
    template = 'admin/edit_inlines/gen_coll_tabular.html'


class MediaAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'caption')}),
        (_("Content"), {'fields': (('file', 'external_url'),)}),
        (_("Credit"), {'fields': ('author', 'one_off_author', 'reproduction_allowed')}),
        (_("Metadata"), {'fields': ('metadata', 'mime_type')}),
        (_("Connections"), {'fields': ('public', 'site')}),
        # (_("Widget"), {'fields': ('width', 'height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug', 'widget_template',)
        }),
    )

    add_fieldsets = (
        (None, {'fields': ('title',)}),
        (_("Content"), {'fields': ('external_url', 'file', 'caption')}),
        (_("Rights"), {'fields': ('public', 'reproduction_allowed')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('slug', 'creation_date', 'site')
        })
    )

    list_display = ('title', 'author_name', 'mime_type', 'public', 'creation_date')
    list_filter = ('site', 'creation_date', 'public')
    list_editable = ('public',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption', 'file')
    raw_id_fields = ('author', )
    add_form_template = 'admin/massmedia/content_add_form.html'

    def get_fieldsets(self, request, obj=None):
        """
        Return add_fieldsets if it is a new object and the form has specified
        different fieldsets for creation vs. change. Otherwise punt.
        """
        if not obj and hasattr(self, 'add_fieldsets'):
            return self.add_fieldsets
        return super(MediaAdmin, self).get_fieldsets(request, obj)

    def get_form(self, request, obj=None, **kwargs):
        """
        Return a special add form if specified
        """
        defaults = {}
        if not obj and hasattr(self, 'add_form'):
            defaults = {
                'form': self.add_form
            }
        defaults.update(kwargs)
        return super(MediaAdmin, self).get_form(request, obj, **defaults)


class ImageAdmin(MediaAdmin):
    list_display = ('render_thumb', 'title', 'creation_date')
    list_display_links = ('render_thumb', 'title', )
    list_editable = tuple()
    add_fieldsets = (
        (_("Content"), {'fields': ('external_url', 'file', 'caption')}),
        (_("Rights"), {'fields': ('public', 'reproduction_allowed')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('title', 'slug', 'creation_date', 'site')
        })
    )
    add_form = ImageCreationForm

    def get_urls(self):
        from django.conf.urls import patterns, url

        urls = super(ImageAdmin, self).get_urls()
        my_urls = patterns('',
            (r'^(?P<image_id>\d+)/crops/add/$', self.add_crop),
            (r'^(?P<image_id>\d+)/crops/(?P<object_id>\d+)/$', self.update_crop),
            (r'^(?P<image_id>\d+)/crops/(?P<object_id>\d+)/delete/$', self.delete_crop),
            url(r'^close/$', self.close_window, name="imagecustomsize_close"),
        )
        return my_urls + urls

    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'file':
            kwargs['widget'] = AdminImageWidget
            kwargs.pop('request')
            return db_field.formfield(**kwargs)
        elif db_field.name == 'external_url':
            kwargs['widget'] = AdminExternalURLWidget
            kwargs.pop('request')
            return db_field.formfield(**kwargs)
        return super(ImageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

    def add_crop(self, request, image_id):
        from massmedia.views import ImageCustomSizeCreate
        return ImageCustomSizeCreate.as_view()(request, image_id=image_id)

    def delete_crop(self, request, image_id, object_id):
        from massmedia.views import ImageCustomSizeDelete
        return ImageCustomSizeDelete.as_view()(request, image_id=image_id, object_id=object_id)

    def update_crop(self, request, image_id, object_id):
        from massmedia.views import ImageCustomSizeUpdate
        return ImageCustomSizeUpdate.as_view()(request, image_id=image_id, object_id=object_id)

    def close_window(self, request):
        from django.views.generic.base import TemplateView
        return TemplateView.as_view(template_name='admin/massmedia/imagecustomsize/close_window.html')(request)


class VideoAdmin(MediaAdmin):
    list_display = ('title', 'thumb', 'author_name', 'mime_type',
                    'public', 'creation_date')
    fieldsets = (
        (None, {'fields': ('title', 'caption')}),
        (_("Content"), {'fields': (('file', 'external_url'), 'thumbnail')}),
        (_("Credit"), {'fields': ('author', 'one_off_author', 'reproduction_allowed')}),
        (_("Metadata"), {'fields': ('metadata', 'mime_type')}),
        (_("Connections"), {'fields': ('public', 'site')}),
        (_("Widget"), {'fields': ('width', 'height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug', 'widget_template',)
        }),
    )

    raw_id_fields = ('thumbnail',)
    add_fieldsets = (
        (None, {'fields': ('title', 'slug',)}),
        (_("Content"), {'fields': (('external_url', 'file'), 'thumbnail')}),
        (_("Rights"), {'fields': ('public', 'reproduction_allowed')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('creation_date', 'site')
        })
    )
    add_form = VideoCreationForm


class AudioAdmin(MediaAdmin, admin.ModelAdmin):
    add_form = AudioCreationForm


class FlashAdmin(MediaAdmin):
    add_form = FlashCreationForm


class DocumentAdmin(MediaAdmin):
    add_form = DocumentCreationForm


class CollectionInline(GenericCollectionTabularInline):
    model = CollectionRelation
    template = 'admin/edit_inline/gen_coll_tabular.html'


class CollectionAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'caption', 'zip_file', 'external_url', 'public', 'site')
    list_display = ('title', 'caption', 'public', 'creation_date')
    list_filter = ('site', 'creation_date', 'public')
    prepopulated_fields = {'slug': ('title', )}
    date_hierarchy = 'creation_date'
    search_fields = ('caption', )
    inlines = (CollectionInline, )

    class Media:
        js = (
            'js/genericcollections.js',
        )


class EmbedAdmin(MediaAdmin):
    fieldsets = (
        (None, {'fields': ('title', 'caption')}),
        (_("Content"), {'fields': (('code', ), )}),
        (_("Credit"), {'fields': ('author', 'one_off_author', 'reproduction_allowed')}),
        (_("Metadata"), {'fields': ('metadata', 'mime_type')}),
        (_("Connections"), {'fields': ('public', 'site')}),
        (_("Widget"), {'fields': ('width', 'height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug', 'widget_template',)
        }),
    )

    add_fieldsets = (
        (_("Content"), {'fields': ('title', 'external_url', 'caption')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('slug', 'creation_date', 'site')
        })
    )

    add_form = EmbedCreationForm

    list_display = ('title', 'mime_type', 'public', 'creation_date')
    list_filter = ('site', 'creation_date', 'public')
    list_editable = ('public',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption', )


admin.site.register(Collection, CollectionAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(Flash, FlashAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Embed, EmbedAdmin)

if not settings.FS_TEMPLATES:
    admin.site.register(MediaTemplate)
