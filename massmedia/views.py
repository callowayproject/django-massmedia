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

def snipshot_callback(request, pk):
    from django.core.files.base import ContentFile
    from urllib import urlopen
    img = get_object_or_404(models.Image, pk=pk)
    if 'fileupload' in request.GET:
        img.file.save(img.file.path, ContentFile(urlopen(request.GET['fileupload']).read()))
    return HttpResponse(str(img.file.size))


def browse(request):
    from django.core import urlresolvers
    path = request.path.strip('/').split('/')
    if len(path) > 1:
        return HttpResponse('You want an %s with an id of %s' % ('idk', path[-1]))
    if not request.GET.has_key('pop'):
        return HttpResponse('Incorrect parameters. Need pop=1')
    getcopy = request.GET.copy()
    if 'type' in getcopy:
        get_type = getcopy['type']
        del getcopy['type']
    else:
        get_type = 'image'
    request.GET = getcopy
    view_func, args, kwargs = urlresolvers.resolve(urlresolvers.reverse("admin:massmedia_%s_changelist" % get_type))
    return view_func(request)

def tinymcepopup_url(request):
    from django.conf import settings
    import os
    tinymce_root = os.path.join(getattr(settings, 'TINYMCE_JS_ROOT', os.path.join(settings.MEDIA_ROOT, 'js', 'tiny_mce')), 'tiny_mce_popup.js')
    
    return HttpResponse(open(tinymce_root, 'r').read(), mimetype="application/javascript")