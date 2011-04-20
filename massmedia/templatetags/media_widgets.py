from django import template
from django.conf import settings
from massmedia.models import Image

register = template.Library()

class MassMediaNode(template.Node):
    def __init__(self, *args):
        assert len(args)
        self.args = list(args)
    
    def render(self, context):
        self.args[0] = context.get(self.args[0],self.args[0])
        if isinstance(self.args[0], basestring):
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
        media.file.url,
        Site.objects.get_current().domain,
        reverse('massmedia_snipshot_callback',None,(media.pk,))
    )
register.simple_tag(snipshot_url)