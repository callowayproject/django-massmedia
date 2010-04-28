import django
from django import forms
from django.contrib.sites.models import Site

from models import Image, Video, Audio, Flash, Document
import datetime

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
    class Meta:
        model = Image

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
