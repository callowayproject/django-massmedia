from django.conf.urls import patterns, url
from django.views.generic.detail import DetailView
from django.views.generic.list import ListView
from django.views.generic.base import TemplateView
from django.http import HttpResponseNotFound
from models import Collection, Image, Video, Audio, Flash, Document, Embed


media_dict = {
    'collection': {
        'queryset': Collection.objects.public(), 'meta': Collection._meta},
    'image': {
        'queryset': Image.objects.public(), 'meta': Image._meta},
    'audio': {
        'queryset': Audio.objects.public(), 'meta': Audio._meta},
    'video': {
        'queryset': Video.objects.public(), 'meta': Video._meta},
    'flash': {
        'queryset': Flash.objects.public(), 'meta': Flash._meta},
    'document': {
        'queryset': Document.objects.public(), 'meta': Document._meta},
    'embed': {
        'queryset': Embed.objects.public(), 'meta': Embed._meta},
}


class MediaIndexView(TemplateView):
    template_name = 'massmedia/index.html'

    def get_context_data(self, **kwargs):
        kwargs['media'] = media_dict
        return super(MediaIndexView, self).get_context_data(**kwargs)


def generic_wrapper(request, *args, **kwargs):
    """
    This allows us to get the mediatype variable from the url and pass the
    correct queryset to the generic view
    """
    if 'mediatype' in kwargs and kwargs['mediatype'] in media_dict:
        mediatype = kwargs.pop('mediatype')
        queryset = media_dict[mediatype]['queryset']
        if 'extra_context' in kwargs:
            kwargs['extra_context'].update({'mediatype': mediatype})
        else:
            kwargs['extra_context'] = {'mediatype': mediatype}
        if 'enlarge' in kwargs:
            kwargs.pop('enlarge')
            kwargs['template_name'] = 'massmedia/enlarge_%s_detail.html' % mediatype
        if 'slug' in kwargs or 'object_id' in kwargs:
            return DetailView.as_view(queryset=queryset)(request, *args, **kwargs)
        if 'template_name' not in kwargs:
            kwargs['template_name'] = 'massmedia/list.html'
        return ListView.as_view(queryset=queryset)(request, *args, **kwargs)
    return HttpResponseNotFound()

urlpatterns = patterns('',
    url(
        r'^$',
        MediaIndexView.as_view(),
        name="massmedia_index"),
    url(
        r'^(?P<enlarge>enlarge)/(?P<mediatype>\w+)/(?P<slug>[-\w]+)/$',
        generic_wrapper,
        name="massmedia_enlarge_detail"),
    url(
        r'^(?P<enlarge>enlarge)/(?P<mediatype>\w+)/(?P<object_id>\d+)/$',
        generic_wrapper,
        name="massmedia_enlarge_detail_pk"),
    url(
        r'^(?P<mediatype>\w+)/$',
        generic_wrapper,
        kwargs={'paginate_by': 15, },
        name='massmediatype_index'),
    url(
        r'^(?P<mediatype>\w+)/(?P<slug>[-\w]+)/$',
        generic_wrapper,
        name="massmedia_detail"),
    url(
        r'^(?P<mediatype>\w+)/(?P<object_id>\d+)/$',
        generic_wrapper,
        name="massmedia_detail_pk"),
    url(
        r'^collection/(?P<slug>[-\w]+)/(?P<type>[-\w]+)/$',
        'massmedia.views.list_by_collection_by_type',
        name="massmedia_collection_by_type"),
    (r'^widget/(?P<id>\d+)/(?P<type>[-\w]+)/$', 'massmedia.views.widget'),
)
