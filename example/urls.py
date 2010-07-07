from django.conf.urls.defaults import *
from django.conf import settings
import os

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^example/', include('example.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),
    url(r'^browse/', 'massmedia.views.browse', name="fb_browse"),
    url(r'^tinymcepopup$', 'massmedia.views.tinymcepopup_url', name="tinymcepopupurl"),
    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),
    
    (r'^static/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': settings.MEDIA_ROOT}),
    
    (r'^mymedia/(?P<path>.*)$', 'django.views.static.serve',
            {'document_root': os.path.join(settings.PROJECT_ROOT,'store_here')}),
    
    (r'^tinymce/', include('tinymce.urls')),
    (r'', include('massmedia.urls'))
)
