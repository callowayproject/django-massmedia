from django.contrib import admin
from django.contrib.admin.widgets import AdminFileWidget
from django.contrib.contenttypes.models import ContentType
from django import template
from django.shortcuts import render_to_response
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext as _

import os

from models import Image,Video,Audio,Flash,Collection,\
    CollectionRelation,MediaTemplate,GrabVideo,Document
import settings
from forms import ImageCreationForm, VideoCreationForm, AudioCreationForm, \
    FlashCreationForm, DocumentCreationForm



class AdminImageWidget(AdminFileWidget):
    def render(self, name, value, attrs=None):
        output = []
        if value and getattr(value, "url", None):
            pcs = os.path.splitext(value.url)
            image_url = "".join([pcs[0], '.thumb', pcs[1]])
            file_name=str(value)
            output.append(u' <a href="%s" target="_blank"><img src="%s" alt="%s" title="%s. Click to see the full-sized image."/></a> %s ' % \
                (value.url, image_url, file_name, file_name, _('Change:')))
        output.append(super(AdminFileWidget, self).render(name, value, attrs))
        return mark_safe(u''.join(output))


class GenericCollectionInlineModelAdmin(admin.options.InlineModelAdmin):
    ct_field = "content_type"
    ct_fk_field = "object_id"
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
    template = 'admin/edit_inline/gen_coll_tabular.html'

class MediaAdmin(admin.ModelAdmin):
    fieldsets = (
        (None, {'fields':('title','caption')}),
        ('Content',{'fields':(('file','external_url'),)}),
        ('Credit',{'fields':('author','one_off_author','credit','reproduction_allowed')}),
        ('Metadata',{'fields':('metadata','mime_type')}),
        ('Connections',{'fields':('public','categories','sites')}),
        ('Widget',{'fields':('width','height')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug','widget_template',)
        }),
    )
    add_fieldsets = (
        (None, {'fields': ('title', 'slug',)}),
        ('Content',{'fields':('external_url','file')}),
        ('Rights', {'fields': ('public','reproduction_allowed')}),
        ('Additional Info', {
            'classes': ('collapse',),
            'fields': ('creation_date', 'sites')
        })
    )
    
    list_display = ('title', 'author_name', 'mime_type', 'public', 'creation_date')
    list_filter = ('sites', 'creation_date','public')
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
    list_display = ('title','thumb','author_name','mime_type','public','creation_date')
    add_fieldsets = (
        (None, {'fields': ('title', 'slug',)}),
        ('Content',{'fields':('external_url','file')}),
        ('Rights', {'fields': ('public','reproduction_allowed')}),
        ('Additional Info', {
            'classes': ('collapse',),
            'fields': ('creation_date', 'sites')
        })
    )
    add_form = ImageCreationForm
    
    def formfield_for_dbfield(self, db_field, **kwargs):
        if db_field.name == 'file':
            kwargs['widget'] = AdminImageWidget
            request = kwargs.pop('request')
            return db_field.formfield(**kwargs)
        return super(ImageAdmin, self).formfield_for_dbfield(db_field, **kwargs)

class VideoAdmin(MediaAdmin):
    list_display = ('title','thumb','author_name','mime_type','public','creation_date')
    fieldsets = (
        (None, {'fields':('title','caption')}),
        ('Content',{'fields':(('file','external_url'),'thumbnail')}),
        ('Credit',{'fields':('author','one_off_author','credit','reproduction_allowed')}),
        ('Metadata',{'fields':('metadata','mime_type')}),
        ('Connections',{'fields':('public','categories','sites')}),
        ('Widget',{'fields':('width','height')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('slug','widget_template',)
        }),
    )
    
    raw_id_fields = ('thumbnail',)
    add_fieldsets = (
        (None, {'fields': ('title', 'slug',)}),
        ('Content',{'fields':(('external_url','file'), 'thumbnail')}),
        ('Rights', {'fields': ('public','reproduction_allowed')}),
        ('Additional Info', {
            'classes': ('collapse',),
            'fields': ('creation_date', 'sites')
        })
    )
    add_form = VideoCreationForm


class GrabVideoAdmin(VideoAdmin):
    search_fields = ('title','caption','keywords')
    list_filter = VideoAdmin.list_filter + ('one_off_author',)
    list_display = ('asset_id','layout_id','title','thumb','one_off_author','public','creation_date','categories')
    fieldsets = ( ('Grab',{'fields':('asset_id','layout_id','keywords')}), )
    for fieldset in VideoAdmin.fieldsets:
        if fieldset[0] == 'Content':
            continue
        fieldsets += (fieldset,)
    
class AudioAdmin(MediaAdmin,admin.ModelAdmin):
    add_form = AudioCreationForm

class FlashAdmin(MediaAdmin):
    add_form = FlashCreationForm

class DocumentAdmin(MediaAdmin):
    add_form = DocumentCreationForm

class CollectionInline(GenericCollectionTabularInline):
    model = CollectionRelation

class CollectionAdmin(admin.ModelAdmin):
    fields = ('title','slug','caption','zip_file','public','categories','sites')
    list_display = ('title','caption', 'public', 'creation_date')
    list_filter = ('sites', 'creation_date','public')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption',)
    inlines = (CollectionInline,)
    class Media:
        js = ('js/genericcollections.js',)

admin.site.register(Collection , CollectionAdmin)
admin.site.register(Image, ImageAdmin)
admin.site.register(Video, VideoAdmin)
admin.site.register(Audio, AudioAdmin)
admin.site.register(Flash, FlashAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(GrabVideo, GrabVideoAdmin)

if not settings.FS_TEMPLATES:
    admin.site.register(MediaTemplate)