import datetime, time, re

from django import template
from django.core.cache import cache
from django.conf import settings as global_settings
from massmedia.youtube import YouTubeFeed

register = template.Library()

CACHE_LENGTH = 3600 #1hour
CALL_LENGTH = 10

def cache_get(key):
    """
    Modified cache getting derived from MintCache 
    http://www.djangosnippets.org/snippets/793/
    
    Since the remote call to google can take several seconds, we don't want a 
    dog pile.
    """
    packed_val = cache.get(key)
    if packed_val is None:
        return None
    try:
        val, refresh_time, refreshed = packed_val
    except:
        if global_settings.DEBUG:
            raise
        else:
            return None
    if (time.time() > refresh_time) and not refreshed:
        # Store the stale value while the cache revalidates for another 
        #   CALL_LENGTH seconds.
        cache_set(key, val, timeout=CALL_LENGTH, refreshed=True)
        return None
    return val


def cache_set(key, val, timeout=CACHE_LENGTH, refreshed=False):
    """
    Modified cache setting derived from MintCache 
    http://www.djangosnippets.org/snippets/793/
    
    Since the remote call to google can take several seconds, we don't want a 
    dog pile.
    """
    refresh_time = timeout + time.time()
    real_timeout = timeout + CALL_LENGTH
    packed_val = (val, refresh_time, refreshed)
    return cache.set(key, packed_val, real_timeout)

class YouTubeFeedNode(template.Node):
    def __init__(self, media_object, varname):
        self.media_object = template.Variable(media_object)
        self.varname = varname
    
    def render(self, context):
        media_object = self.media_object.resolve(context)
        playlist_id = media_object.external_url.split("/")[-1]
        cache_key = "get_youtube_feed.%s" % playlist_id
        cache_results = cache_get(cache_key)
        
        if cache_results:
            context[self.varname] = cache_results
            return ''
        
        try:
            # In the event something unexpected happens with retrieving 
            # the video feed, set the feed to None. 
            feed = YouTubeFeed(media_object.external_url)
        except:
            feed = None
        cache_set(cache_key, feed)
        context[self.varname] = feed
        return ''

def get_youtube_feed(parser, token):
    """
    Returns a You Tube Feed object
    
    Usage:
        {% get_youtube_feed <media object> as varname %}
    """
    bits = token.contents.split()
    if len(bits) != 4:
        raise template.TemplateSyntaxError("%s Tag is called: {%% %s <media object> as varname %%}" % (bits[0], bits[0]))
    return YouTubeFeedNode(bits[1], bits[3])

class SplitNode(template.Node):
    def __init__(self, varstring, varname, split_string=None):
        self.varstring = template.Variable(varstring)
        self.varname = varname
        self.split_string = split_string
    
    def render(self, context):
        try:
            varstring = self.varstring.resolve(context)
        except template.VariableDoesNotExist:
            varstring = self.varstring.var
        
        if self.split_string is None:
            context[self.varname] = varstring.split()
        else:
            context[self.varname] = varstring.split(self.split_string)
        return ''
    
    
def split(parser, token):
    """
    Splits string into a list
    
    Usage:
        {% split "1,2,3,4" as var %}
        {% split "1, 2, 3, 4" ", " as var %}
        {% split contextvar as var %}
    """
    bits = token.split_contents()
    if len(bits) == 4 and bits[2] == 'as':
        return SplitNode(bits[1], bits[3])
    elif len(bits) == 5 and bits[3] == 'as':
        return SplitNode(bits[1], bits[4], bits[2].strip('"').strip("'"))
    else:
        raise template.TemplateSyntaxError("%s Tag is called: {%% %s <string or variable> [<split string>] as varname %%}" % (bits[0], bits[0]))

class Duration(object):
    """A duration in seconds"""
    def __init__(self, value):
        super(Duration, self).__init__()
        seconds = int(value)
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.hour = hours
        self.minute = minutes
        self.second = seconds

@register.filter
def format_seconds(value, arg=None):
    """Formats a number of seconds according to the given format."""
    from django.utils import dateformat
    #from django.utils import formats
    if value in (None, u''):
        return u''
    if arg is None:
        arg = settings.TIME_FORMAT
    data = Duration(value)
    
    try:
        return dateformat.time_format(data, arg)
    except AttributeError:
        return ''
time.is_safe = False


register.tag(get_youtube_feed)
register.tag(split)