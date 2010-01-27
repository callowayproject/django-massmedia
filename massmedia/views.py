from massmedia import models
from massmedia.templatetags.media_widgets import show_media
from tagging.models import TaggedItem,Tag
from django.template import RequestContext
from django.shortcuts import render_to_response,get_object_or_404
from django.conf import settings
from django.http import Http404,HttpResponse
from django.contrib.contenttypes.models import ContentType
from django.core.serializers import serialize

def widget(request, id, type):
    try:
        assert hasattr(models,type.capitalize())
        model = getattr(models,type.capitalize())
    except AssertionError:
        raise Http404
    try:
        return render_to_response('massmedia/inline.html',{
            'media':model.objects.get(pk=id),
            'type':type
        }, context_instance=RequestContext(request))
    except model.DoesNotExist:
        return HttpResponse('%s #%s not found'%(type,id))

def list_by_type(request,type):
    try:
        assert hasattr(models,type.capitalize())
        model = getattr(models,type.capitalize())
    except AssertionError:
        raise Http404
    return render_to_response('massmedia/list.html',{
        'objects': model.objects.filter(
            public=True,
            sites__id__exact=settings.SITE_ID
        )
    }, context_instance=RequestContext(request))

def list_by_collection(request,id):
    return render_to_response('massmedia/list.html',{
        'objects': [x.content_object for x in models.CollectionRelation.objects.filter(
            collection=get_object_or_404(models.Collection, pk=id),
            collection__public=True,
            collection__sites__id__exact=settings.SITE_ID
        )]
    }, context_instance=RequestContext(request))

def list_by_collection_by_type(request,id,type):
    return render_to_response('massmedia/list.html',{
        'objects': [x.content_object for x in models.CollectionRelation.objects.filter(
            collection=get_object_or_404(models.Collection, pk=id),
            collection__public=True,
            collection__sites__id__exact=settings.SITE_ID,
            content_type=ContentType.objects.get(name=type),
        )]
    }, context_instance=RequestContext(request))
    
def list(request):
    return render_to_response('massmedia/list_types.html',{
        'collections':models.Collection.objects.filter(
            public=True,
            sites__id__exact=settings.SITE_ID
        )
    }, context_instance=RequestContext(request))
    
def grab_categorized(request):
    videos = models.GrabVideo.objects.filter(public=True)
    if request.GET.get('author',None):
        videos = videos.filter(one_off_author__iexact=request.GET['author'])
    if request.GET.get('category',None):
        videos = videos.filter(categories__icontains=str(request.GET['category']).lower())
    if request.GET.get('keyword',None):
        videos = videos.filter(keywords__icontains=request.GET['keyword'])
    videos = videos[int(request.GET.get('off',0)):int(request.GET.get('lim',7))]
    if 'layout' in request.GET:
        [setattr(v, 'layout_id', request.GET['layout']) for v in videos]
    if 'width' in request.GET:
        [setattr(v, 'width', request.GET['width']) for v in videos]
    if 'height' in request.GET:
        [setattr(v, 'height', request.GET['height']) for v in videos]
    if 'ajax' in request.GET:
        return render_to_response('massmedia/grab_list.ajax',{
                'videos': videos,
            }, context_instance=RequestContext(request))
    return render_to_response('massmedia/grab_list.html',{
        'videos': videos,
    }, context_instance=RequestContext(request))
        
def snipshot_callback(request, pk):
    from django.core.files.base import ContentFile
    from urllib import urlopen
    img = get_object_or_404(models.Image, pk=pk)
    if 'fileupload' in request.GET:
        img.file.save(img.file.path, ContentFile(urlopen(request.GET['fileupload']).read()))
    return HttpResponse(str(img.file.size))