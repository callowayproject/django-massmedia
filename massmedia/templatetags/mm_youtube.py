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
        feed = YouTubeFeed(media_object.external_url)
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
    
register.tag(get_youtube_feed)
