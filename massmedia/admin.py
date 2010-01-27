from django.contrib import admin
from massmedia.models import Image,Video,Audio,Flash,Collection,\
    CollectionRelation,MediaTemplate,GrabVideo,Document
from django.contrib.contenttypes.models import ContentType
from django.template.defaultfilters import slugify
from massmedia import settings

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

class MediaAdmin(object):
    fieldsets = (
        (None, {'fields':('title','slug','caption')}),
        ('Credit',{'fields':('author','one_off_author','credit','reproduction_allowed')}),
        ('Metadata',{'fields':('metadata','mime_type')}),
        ('Content',{'fields':('external_url','file')}),
        ('Connections',{'fields':('public','categories','sites')}),
        ('Widget',{'fields':('width','height')}),
        ('Advanced options', {
            'classes': ('collapse',),
            'fields': ('widget_template',)
        }),
    )
    list_display = ('title', 'author', 'mime_type', 'public', 'creation_date')
    list_filter = ('sites', 'creation_date','public')
    prepopulated_fields = {'slug': ('title',)}
    date_hierarchy = 'creation_date'
    search_fields = ('caption', 'file')


class ImageAdmin(MediaAdmin,admin.ModelAdmin):
    list_display = ('title','thumb','author','mime_type','metadata','public','creation_date')

class VideoAdmin(MediaAdmin,admin.ModelAdmin):
    list_display = ('title','thumb','author','mime_type','metadata','public','creation_date')
    fieldsets = MediaAdmin.fieldsets + ( ('Thumbnail',{'fields':('thumbnail',)}), )
    raw_id_fields = ('thumbnail',)

class GrabVideoAdmin(VideoAdmin):
    search_fields = ('title','caption','keywords')
    list_filter = VideoAdmin.list_filter + ('one_off_author',)
    list_display = ('asset_id','layout_id','title','thumb','one_off_author','public','creation_date','categories')
    fieldsets = ( ('Grab',{'fields':('asset_id','layout_id','keywords')}), )
    for fieldset in VideoAdmin.fieldsets:
        if fieldset[0] == 'Content':
            continue
        fieldsets += (fieldset,)
    
class AudioAdmin(MediaAdmin,admin.ModelAdmin): pass
class FlashAdmin(MediaAdmin,admin.ModelAdmin): pass
class DocumentAdmin(MediaAdmin,admin.ModelAdmin): pass

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

if settings.TEMPLATE_MODE == 0:
    admin.site.register(MediaTemplate)