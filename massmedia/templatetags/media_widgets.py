from django import template
from django.conf import settings
from massmedia.models import GrabVideo,Image
#from sorl.thumbnail.main import DjangoThumbnail
register = template.Library()

from massmedia.settings import MOGRIFY_KEY

import os

try:
    from hashlib import sha1 as sha
except ImportError:
    from sha import sha

class ThumbnailNode(template.Node):
    """
    A replacement for sorl-thumbnail's thumbnail tag that takes the object's
    storage into account.
    """
    def __init__(self, source_var, size_var, opts=None,
                 context_name=None, **kwargs):
        self.source_var = source_var
        self.size_var = size_var
        self.opts = opts
        self.context_name = context_name
        self.kwargs = kwargs
    
    def render(self, context):
        # Note that this isn't a global constant because we need to change the
        # value for tests.
        try:
            # A file object will be allowed in DjangoThumbnail class
            source = self.source_var.resolve(context)
            if isinstance(source, basestring):
                relative_source = source
        except VariableDoesNotExist:
                source = None
                relative_source = None
        try:
            requested_size = self.size_var.resolve(context)
        except VariableDoesNotExist:
            requested_size = None
        # Size variable can be either a tuple/list of two integers or a valid
        # string, only the string is checked.
        else:
            if isinstance(requested_size, basestring):
                m = size_pat.match(requested_size)
                if m:
                    requested_size = (int(m.group(1)), int(m.group(2)))
                else:
                    requested_size = None
        if relative_source is None or requested_size is None:
            thumbnail = ''
        else:
            try:
                kwargs = {}
                for key, value in self.kwargs.items():
                    kwargs[key] = value.resolve(context)
                opts = dict([(k, v and v.resolve(context))
                             for k, v in self.opts.items()])
                thumbnail = DjangoThumbnail(relative_source, requested_size,
                                opts=opts, processors=PROCESSORS, **kwargs)
            except:
                thumbnail = ''
        # Return the thumbnail class, or put it on the context
        if self.context_name is None:
            return thumbnail
        # We need to get here so we don't have old values in the context
        # variable.
        context[self.context_name] = thumbnail
        return ''
    

class MassMediaNode(template.Node):
    def __init__(self, *args):
        assert len(args)
        self.args = list(args)
    
    def render(self, context):
        self.args[0] = context.get(self.args[0],self.args[0])
        if isinstance(self.args[0], basestring):
            try:
                self.args[0] = GrabVideo.objects.get(slug=self.args[0])
            except GrabVideo.DoesNotExist:
                return ''
        try:
            self.args[0].layout_id = self.args[1]
        except IndexError:
            pass
        return self.args[0].get_template().render(
            template.RequestContext(context['request'], {
                'media':self.args[0],
            })
        )

def show_media(parser, token):
    """
    Renders inclusion template for media
    
    Usage:
        {% show_media <media object> [<alternate layout>] %}
    
    Example:
        {% show_media grabvideo 10101 %}
    """
    return MassMediaNode(*token.contents.split()[1:])
    
register.tag(show_media)

def snipshot_url(media):
    assert isinstance(media, Image)
    from urllib import quote
    from django.contrib.sites.models import Site
    from django.core.urlresolvers import reverse
    return 'http://services.snipshot.com/?snipshot_input=%s&snipshot_callback=http%%3A//%s%s&snipshot_output=fileupload&snipshot_callback_agent=user' % (
        quote(media.get_absolute_url()),
        Site.objects.get_current().domain,
        reverse('massmedia_snipshot_callback',None,(media.pk,))
    )
register.simple_tag(snipshot_url)