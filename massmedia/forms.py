import django
from django import forms
from django.contrib.sites.models import Site
import os, datetime

from models import Image, Video, Audio, Flash, Document


class ContentCreationForm(forms.ModelForm):
    """
    A form that creates a piece of content from a file and title.
    """
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size':85}))
    external_url = forms.URLField(
        required=False,
        help_text="If this URLField is set, the media will be pulled externally")
    file = forms.FileField(required=False)
    creation_date = forms.DateTimeField()
    
    def __init__(self, data=None, files=None, auto_id='id_%s', prefix=None,
                     initial=None, error_class=forms.util.ErrorList, label_suffix=':',
                     empty_permitted=False, instance=None):
        # set a default creation date and add the current site
        if not instance and (initial is not None and not initial.has_key('creation_date')):
            initial['creation_date'] = datetime.datetime.now()
        if not instance and (initial is not None and not initial.has_key('site')):
            initial['site'] = Site.objects.get_current().id
        
        super(ContentCreationForm, self).__init__(data, files, auto_id, prefix, initial, 
                                        error_class, label_suffix, 
                                        empty_permitted, instance)


class ImageCreationForm(ContentCreationForm):
    title = forms.CharField(max_length=255, widget=forms.TextInput(attrs={'size':85}), required=False)
    slug = forms.CharField(required=False)
    file = forms.FileField(required=False)
    class Meta:
        model = Image
    
    def set_title_and_slug(self):
        """
        If the title is empty, set it to the name of the uploaded or external file
        """
        from django.template.defaultfilters import slugify

        if not self.cleaned_data['title']:
            filepath = self.cleaned_data['file'] or self.cleaned_data['external_url'].split('?')[0]
            filename = os.path.basename(filepath)
            self.cleaned_data['title'] = filename
        
        if not self.cleaned_data['slug']:
            slug = slugify(self.cleaned_data['title'])
        
        try:
            Image.objects.get(slug=slug)
            slug = "%s_%d" % (slug, datetime.datetime.now().toordinal())
        except Image.DoesNotExist:
            pass
        self.cleaned_data['slug'] = slug
    
    
    def clean(self):
        self.set_title_and_slug()
        return super(ImageCreationForm, self).clean()

class VideoCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Video

class AudioCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Audio

class FlashCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Flash

class DocumentCreationForm(ContentCreationForm, forms.ModelForm):
    class Meta:
        model = Document
