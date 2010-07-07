from massmedia import models

from django.contrib.contenttypes.models import ContentType
from django.core.xheaders import populate_xheaders
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404,HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response,get_object_or_404
from django.template import RequestContext
from django.views.decorators.cache import cache_page

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


def list_by_collection_by_type(request, slug, type):
    ctype = get_object_or_404(ContentType, name=type)
    return render_to_response('massmedia/list.html',{
        'objects': [x.content_object for x in models.CollectionRelation.objects.filter(
            collection=get_object_or_404(models.Collection, slug=slug),
            content_type=ctype,
        )]
    }, context_instance=RequestContext(request))


def mediatype_detail(request, queryset, object_id=None, slug=None,
            slug_field='slug', template_name=None, template_name_field=None,
            template_loader=None, extra_context=None,
            context_processors=None, template_object_name='object',
            mimetype=None):
    
    if extra_context is None: extra_context = {}
    model = queryset.model
    if object_id:
        queryset = queryset.filter(pk=object_id)
    elif slug and slug_field:
        queryset = queryset.filter(**{slug_field: slug})
    else:
        raise AttributeError("Generic media detail view must be called with either an object_id or a slug/slug_field.")
    try:
        obj = queryset.get()
    except ObjectDoesNotExist:
        raise Http404("No %s found matching the query" % (model._meta.verbose_name))
    t = obj.get_template()
    c = RequestContext(request, {
        'media': obj,
    }, context_processors)
    for key, value in extra_context.items():
        if callable(value):
            c[key] = value()
        else:
            c[key] = value
    response = HttpResponse(t.render(c), mimetype=mimetype)
    populate_xheaders(request, response, model, getattr(obj, obj._meta.pk.name))
    return response
    
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