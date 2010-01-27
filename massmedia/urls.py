from django.conf.urls.defaults import *
from models import GrabVideo

urlpatterns = patterns('',
    (r'^type/(?P<type>[-\w]+)/$', 'massmedia.views.list_by_type'),
    (r'^collection/(?P<id>\d+)/(?P<type>[-\w]+)/$', 'massmedia.views.list_by_collection_by_type'),
    (r'^collection/(?P<id>\d+)/$', 'massmedia.views.list_by_collection'),
    (r'^widget/(?P<id>\d+)/(?P<type>[-\w]+)/$','massmedia.views.widget'),
    url(r'^snipshot/(?P<pk>\d+)/$', 'massmedia.views.snipshot_callback', name='massmedia_snipshot_callback'),
    url(r'^grab/(?P<object_id>\d+)/$','django.views.generic.list_detail.object_detail',{'queryset':GrabVideo.objects.filter(public=True)}),
    (r'^grab/$','massmedia.views.grab_categorized'),
    (r'','massmedia.views.list'),
)
