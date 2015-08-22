import datetime
import os

from django import forms
from django.contrib.sites.models import Site

from models import Image, Video, Audio, Flash, Document, Embed


class ContentCreationForm(forms.Form):
    """
    A form that creates a piece of content from a file and title.
    """
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'size': 85}),
        required=False)
    slug = forms.CharField(required=False)
    external_url = forms.URLField(
        required=False,
        help_text="If this URLField is set, the media will be pulled externally")
    file = forms.FileField(required=False)
    creation_date = forms.DateTimeField()

    class Meta:
        fields = ('title', 'slug', 'file', 'external_url', 'creation_date')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=forms.utils.ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):
        # set a default creation date and add the current site
        if not instance and (initial is not None and
                             'creation_date' not in initial):
            initial['creation_date'] = datetime.datetime.now()
        if not instance and (initial is not None and
                             'site' not in initial):
            initial['site'] = Site.objects.get_current().id

        super(ContentCreationForm, self).__init__(data, files, auto_id, prefix, initial,
                                        error_class, label_suffix,
                                        empty_permitted, instance)

    def set_title_and_slug(self):
        """
        If the title is empty, set it to the name of the uploaded or external file
        """
        from django.template.defaultfilters import slugify

        if not self.cleaned_data.get('title', False):
            if 'file' in self.cleaned_data and hasattr(self.cleaned_data['file'], 'name'):
                filename = self.cleaned_data['file'].name
            elif self.cleaned_data.get('external_url', False):
                filepath = self.cleaned_data['external_url'].split('?')[0]
                filename = os.path.basename(filepath)
            else:
                return
            self.cleaned_data['title'] = filename

        if not self.cleaned_data.get('slug', False):
            slug = slugify(self.cleaned_data['title'])
        else:
            slug = self.cleaned_data['slug']
        try:
            self._meta.model.objects.get(slug=slug)
            slug = "%s_%d" % (slug, datetime.datetime.now().toordinal())
        except self._meta.model.DoesNotExist:
            pass
        self.cleaned_data['slug'] = slug

    def clean(self):
        self.set_title_and_slug()
        return super(ContentCreationForm, self).clean()


class ImageCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Image
        fields = ('external_url', 'file', 'caption', 'public', 'reproduction_allowed', 'title', 'slug', 'creation_date', 'site')


class VideoCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Video
        fields = ('title', 'slug', 'file', 'external_url', 'creation_date')


class AudioCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Audio
        fields = ('title', 'slug', 'file', 'external_url', 'creation_date')


class FlashCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Flash
        fields = ('title', 'slug', 'file', 'external_url', 'creation_date')


class DocumentCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Document
        fields = ('title', 'slug', 'file', 'external_url', 'creation_date')


class EmbedCreationForm(forms.ModelForm):
    """
    A form that creates a piece of content from a file and title.
    """
    title = forms.CharField(
        max_length=255,
        widget=forms.TextInput(attrs={'size': 85}))
    external_url = forms.URLField(
        required=False,
        help_text="If this URLField is set, the media will be pulled externally")
    code = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'size': 85}))
    creation_date = forms.DateTimeField()

    class Meta:
        model = Embed
        fields = ('title', 'external_url', 'code', 'creation_date')

    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                 initial=None, error_class=forms.utils.ErrorList,
                 label_suffix=':', empty_permitted=False, instance=None):
        # set a default creation date and add the current site
        if not instance and (initial is not None and
                             'creation_date' not in initial):
            initial['creation_date'] = datetime.datetime.now()
        if not instance and (initial is not None and
                             'site' not in initial):
            initial['site'] = Site.objects.get_current().id

        super(EmbedCreationForm, self).__init__(data, files, auto_id, prefix, initial,
                                        error_class, label_suffix,
                                        empty_permitted, instance)
