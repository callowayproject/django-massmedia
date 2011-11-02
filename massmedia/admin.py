from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget, AdminURLFieldWidget
from django.contrib.contenttypes.models import ContentType
from django.http import HttpResponse
from django import template
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _
from django.utils.html import escape

import os

from models import (Image, Video, Audio, Flash, Collection, Embed, Document,
    CollectionRelation, MediaTemplate)
import settings
from forms import (ImageCreationForm, VideoCreationForm, AudioCreationForm, 
    FlashCreationForm, DocumentCreationForm, EmbedCreationForm)

from templatetags.media_widgets import snipshot_url

class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        try:
            thumbnail = value.instance.thumbnail.url
            width = value.instance.thumb_width
            height = value.instance.thumb_height
            snipshot = snipshot_url(value.instance)
            crop_tag = '''<br /><a class="link" href="#" onclick="var win = window.open('%s','snipshot', 'height=500,width=800,resizable=yes,scrollbars=yes');win.focus();">Crop image with snipshot</a>'''%snipshot
            tag = u'<img src="%s" width="%s" height="%s"/>' % (thumbnail, width, height)
        except:
            crop_tag = u""
            tag = _("<strong>No Thumbnail available</strong>")
        if value:
            file_name=str(value)
            output.append(u'<a href="%s" target="_blank">%s</a>' % (value.url, tag))
            output.append(crop_tag)
        return mark_safe(u''.join(output))

class AdminExternalURLWidget(AdminURLFieldWidget):
    def render(self, name, value, attrs=None):
        output = []
        tag = _("<strong>No Thumbnail available</strong>")
        if value:
            file_name=str(value)
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
        (None, {'fields':('title', 'caption')}),
        (_("Content"), {'fields':(('file', 'external_url'),)}),
        (_("Credit"), {'fields':('author', 'one_off_author', 'reproduction_allowed')}),
        (_("Metadata"), {'fields':('metadata', 'mime_type')}),
        (_("Connections"), {'fields':('public', 'site')}),
        (_("Widget"), {'fields':('width', 'height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug', 'widget_template',)
        }),
    )
    
    if settings.USE_TAGGING:
        fieldsets[4][1]['fields'] += ('categories',)
    
    add_fieldsets = (
        (None, {'fields': ('title',)}),
        (_("Content"),{'fields':('external_url','file', 'caption')}),
        (_("Rights"), {'fields': ('public','reproduction_allowed')}),
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
    
    
    def render_change_form(self, request, context, add=False, change=False, form_url='', obj=None):
        opts = self.model._meta
        app_label = opts.app_label
        ordered_objects = opts.get_ordered_objects()
        is_popup = '_popup' in request.REQUEST or 'pop' in request.REQUEST
        context.update({
            'add': add,
            'change': change,
            'has_add_permission': self.has_add_permission(request),
            'has_change_permission': self.has_change_permission(request, obj),
            'has_delete_permission': self.has_delete_permission(request, obj),
            'has_file_field': True, # FIXME - this should check if form or formsets have a FileField,
            'has_absolute_url': hasattr(self.model, 'get_absolute_url'),
            'ordered_objects': ordered_objects,
            'form_url': mark_safe(form_url),
            'opts': opts,
            'content_type_id': ContentType.objects.get_for_model(self.model).id,
            'save_as': self.save_as,
            'save_on_top': self.save_on_top,
            'root_path': self.admin_site.root_path,
            'is_popup': is_popup,
        })
        context_instance = template.RequestContext(request, current_app=self.admin_site.name)
        if add:
            return render_to_response(self.add_form_template or [
                "admin/%s/%s/add_form.html" % (app_label, opts.object_name.lower()),
                "admin/%s/add_form.html" % app_label,
                "admin/change_form.html"
            ], context, context_instance=context_instance)
        else:
            return render_to_response(self.change_form_template or [
                "admin/%s/%s/change_form.html" % (app_label, opts.object_name.lower()),
                "admin/%s/change_form.html" % app_label,
                "admin/change_form.html"
            ], context, context_instance=context_instance)
    

class ImageAdmin(MediaAdmin):
    list_display = ('render_thumb','title','creation_date')
    list_display_links = ('render_thumb','title',)
    list_editable = tuple()
    add_fieldsets = (
        (_("Content"),{'fields':('external_url','file','caption')}),
        (_("Rights"), {'fields': ('public','reproduction_allowed')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('title', 'slug', 'creation_date', 'site')
        })
    )
    add_form = ImageCreationForm
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'file':
            kwargs['widget'] = AdminImageWidget
            request = kwargs.pop('request')
            return db_field.formfield(**kwargs)
        elif db_field.name == 'external_url':
            kwargs['widget'] = AdminExternalURLWidget
            request = kwargs.pop('request')
            return db_field.formfield(**kwargs)
        return super(ImageAdmin, self).formfield_for_dbfield(db_field, **kwargs)
    
    def response_add(self, request, obj, post_url_continue='../%s/'):
        """
        Determines the HttpResponse for the add_view stage.
        
        Returns a different result only if pop=2
        """
        if request.GET.has_key('pop'):
            pk_value = obj._get_pk_val()
            return HttpResponse('<script type="text/javascript">opener.myDismissAddAnotherPopup(window, "%s", "%s");</script>' % \
                # escape() calls force_unicode.
                (escape(pk_value), escape(obj)))
        else:
            return super(ImageAdmin, self).response_add(request, obj, post_url_continue)
    

class VideoAdmin(MediaAdmin):
    list_display = ('title','thumb','author_name','mime_type','public','creation_date')
    fieldsets = (
        (None, {'fields':('title','caption')}),
        (_("Content"),{'fields':(('file','external_url'),'thumbnail')}),
        (_("Credit"),{'fields':('author','one_off_author','reproduction_allowed')}),
        (_("Metadata"),{'fields':('metadata','mime_type')}),
        (_("Connections"),{'fields':('public','site')}),
        (_("Widget"),{'fields':('width','height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug','widget_template',)
        }),
    )
    
    if settings.USE_TAGGING:
        fieldsets[4][1]['fields'] += ('categories',)
    
    raw_id_fields = ('thumbnail',)
    add_fieldsets = (
        (None, {'fields': ('title', 'slug',)}),
        (_("Content"),{'fields':(('external_url','file'), 'thumbnail')}),
        (_("Rights"), {'fields': ('public','reproduction_allowed')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('creation_date', 'site')
        })
    )
    add_form = VideoCreationForm

class AudioAdmin(MediaAdmin,admin.ModelAdmin):
    add_form = AudioCreationForm

class FlashAdmin(MediaAdmin):
    add_form = FlashCreationForm

class DocumentAdmin(MediaAdmin):
    add_form = DocumentCreationForm

class CollectionInline(GenericCollectionTabularInline):
    model = CollectionRelation

class CollectionAdmin(admin.ModelAdmin):
    fields = ('title', 'slug', 'caption', 'zip_file', 'external_url', 'public', 'site')
    list_display = ('title','caption', 'public', 'creation_date')
    list_filter = ('site', 'creation_date','public')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption',)
    inlines = (CollectionInline,)
    
    if settings.USE_TAGGING:
        fields += ('categories',)
    
    class Media:
        js = (
            'http://code.jquery.com/jquery-1.4.2.min.js',
            'http://ajax.googleapis.com/ajax/libs/jqueryui/1.8.2/jquery-ui.min.js',
            'js/genericcollections.js',
        )

class EmbedAdmin(MediaAdmin):
    fieldsets = (
        (None, {'fields':('title', 'caption')}),
        (_("Content"), {'fields':(('external_url', 'code',),)}),
        (_("Credit"), {'fields':('author', 'one_off_author', 'reproduction_allowed')}),
        (_("Metadata"), {'fields':('metadata', 'mime_type')}),
        (_("Connections"), {'fields':('public', 'site')}),
        (_("Widget"), {'fields':('width', 'height')}),
        (_("Advanced options"), {
            'classes': ('collapse',),
            'fields': ('slug', 'widget_template',)
        }),
    )
    
    add_fieldsets = (
        (_("Content"),{'fields':('title', 'external_url', 'caption')}),
        (_("Additional Info"), {
            'classes': ('collapse',),
            'fields': ('slug', 'creation_date', 'site')
        })
    )
    
    add_form = EmbedCreationForm
    
    if settings.USE_TAGGING:
        fieldsets[4][1]['fields'] += ('categories',)
    
    list_display = ('title', 'mime_type', 'public', 'creation_date')
    list_filter = ('site', 'creation_date', 'public')
    list_editable = ('public',)
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption', )


admin.site.register(Collection , CollectionAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(Flash, FlashAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(Embed, EmbedAdmin)

if not settings.FS_TEMPLATES:
    admin.site.register(MediaTemplate)