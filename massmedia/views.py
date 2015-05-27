from massmedia import models

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
from django.views.generic import CreateView, DeleteView, UpdateView
import simplejson
from django.core.urlresolvers import reverse

from django.conf import settings

from .forms import ContentCreationForm


def widget(request, id, type):
    try:
        assert hasattr(models, type.capitalize())
        model = getattr(models, type.capitalize())
    except AssertionError:
        raise Http404
    try:
        return render_to_response('massmedia/inline.html', {
            'media': model.objects.get(pk=id),
            'type': type
        }, context_instance=RequestContext(request))
    except model.DoesNotExist:
        return HttpResponse('%s #%s not found' % (type, id))


def list_by_collection_by_type(request, slug, type):
    ctype = get_object_or_404(ContentType, name=type)
    return render_to_response('massmedia/list.html', {
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

    if extra_context is None:
        extra_context = {}
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
    return response


def browse(request):
    from django.core import urlresolvers
    path = request.path.strip('/').split('/')
    if len(path) > 1:
        return HttpResponse('You want an %s with an id of %s' % ('idk', path[-1]))
    if 'pop' not in request.GET:
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


def response_mimetype(request):
    if "application/json" in request.META['HTTP_ACCEPT']:
        return "application/json"
    else:
        return "text/plain"


class ContentCreateView(CreateView):
    form = ContentCreationForm

    def form_valid(self, form):
        self.object = form.save()
        f = self.request.FILES.get('file')
        data = [{
            'name': f.name,
            'url': settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"),
            'thumbnail_url': settings.MEDIA_URL + "pictures/" + f.name.replace(" ", "_"),
            'delete_url': reverse('upload-delete', args=[self.object.id]),
            'delete_type': "DELETE"
        }]
        response = JSONResponse(data, {}, response_mimetype(self.request))
        response['Content-Disposition'] = 'inline; filename=files.json'
        return response

    def get_context_data(self, **kwargs):
        context = super(ContentCreateView, self).get_context_data(**kwargs)
        context['pictures'] = models.Image.objects.all()
        return context


class ImageDeleteView(DeleteView):
    model = models.Image

    def delete(self, request, *args, **kwargs):
        """
        This does not actually delete the file, only the database record.  But
        that is easy to implement.
        """
        self.object = self.get_object()
        self.object.delete()
        if request.is_ajax():
            response = JSONResponse(True, {}, response_mimetype(self.request))
            response['Content-Disposition'] = 'inline; filename=files.json'
            return response
        else:
            return HttpResponseRedirect('/upload/new')


class JSONResponse(HttpResponse):
    """JSON response class."""
    def __init__(self, obj='', json_opts={}, mimetype="application/json", *args, **kwargs):
        content = simplejson.dumps(obj, **json_opts)
        super(JSONResponse, self).__init__(content, mimetype, *args, **kwargs)


class ImageCustomSizeCreate(CreateView):
    template_name = 'admin/massmedia/imagecustomsize/change_form.html'

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(ImageCustomSizeCreate, self).get_form_kwargs()
        kwargs.update({'instance': self.get_object()})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(ImageCustomSizeCreate, self).get(request, *args, **kwargs)

    def get_object(self, queryset=None):
        image_id = self.kwargs.get('image_id')
        if image_id is None and len(self.args):
            image_id = int(self.args[0])
        image = get_object_or_404(models.Image, ('id', image_id))
        return models.ImageCustomSize(image=image)

    def get_queryset(self):
        image_id = self.kwargs.get('image_id')
        image = get_object_or_404(models.Image, ('id', image_id))
        return image.custom_sizes.all()

    def get_success_url(self):
        image_id = self.kwargs.get('image_id')
        if image_id:
            return reverse('admin:imagecustomsize_close')
        else:
            return reverse('admin:massmedia_image_changelist')


class ImageCustomSizeUpdate(UpdateView):
    template_name = 'admin/massmedia/imagecustomsize/change_form.html'

    def get_form_kwargs(self):
        """
        Returns the keyword arguments for instantiating the form.
        """
        kwargs = super(models.ImageCustomSizeUpdate, self).get_form_kwargs()
        kwargs.update({'instance': self.get_object()})
        return kwargs

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()
        return super(models.ImageCustomSizeUpdate, self).get(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        """
        Handles POST requests, instantiating a form instance with the passed
        POST variables and then checked for validity.
        """
        if '_cancel' in self.request.POST:
            return HttpResponseRedirect(self.get_success_url())
        self.object = self.get_object()
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            return self.form_valid(form)
        else:
            return self.form_invalid(form)

    def get_object(self, queryset=None):
        object_id = self.kwargs.get('object_id')
        return get_object_or_404(models.ImageCustomSize, ('id', object_id))

    def get_queryset(self):
        image_id = self.kwargs.get('image_id')
        image = get_object_or_404(models.Image, ('id', image_id))
        return image.custom_sizes.all()

    def get_success_url(self):
        image_id = self.kwargs.get('image_id')
        if image_id:
            return reverse('admin:imagecustomsize_close')
        else:
            return reverse('admin:massmedia_image_changelist')


class ImageCustomSizeDelete(DeleteView):
    template_name = 'admin/massmedia/imagecustomsize/confirm_delete.html'

    def get_object(self, queryset=None):
        object_id = self.kwargs.get('object_id')
        print object_id, models.ImageCustomSize.objects.values_list('id', flat=True)
        return get_object_or_404(models.ImageCustomSize, ('id', object_id))

    def get_queryset(self):
        image_id = self.kwargs.get('image_id')
        image = get_object_or_404(models.Image, ('id', image_id))
        return image.custom_sizes.all()

    def get_success_url(self):
        image_id = self.kwargs.get('image_id')
        if image_id:
            return reverse('admin:imagecustomsize_close')
        else:
            return reverse('admin:massmedia_image_changelist')
