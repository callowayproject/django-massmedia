from gdata.youtube.service import YouTubeService, YOUTUBE_PLAYLIST_FEED_URI
from massmedia import settings

class YouTubeBase(object):
    """
    A simple class to get the info for a youtube feed
    """
    
    def __init__(self, url=None):
        self.url = url
        self._service = None
        self.metadata = {}
        self.entries = []
        self.process_url()
    
    def process_url(self):
        """
        Overridden by subclasses
        """
        pass
    
    def get_service(self):
        """
        Return the cached service object or get it and cache it.
        """
        if self._service is None:
            self._service = YouTubeService()
            self._service.email = settings.SERVICES['YOUTUBE']['EMAIL']
            self._service.password = settings.SERVICES['YOUTUBE']['PASSWORD']
            self._service.ProgrammaticLogin()
        return self._service
    
    @staticmethod
    def get_url_from_links(link_list, rel):
        """
        From a list of link elements, return the url for the given rel type
        """
        for item in link_list:
            if item.rel == rel:
                return item.href
    
    @staticmethod
    def get_default_content(content_list):
        """
        return the default content from a content list
        """
        for fmt in content_list:
            if 'isDefault' in fmt.extension_attributes:
                return fmt
    
    @staticmethod
    def get_biggest_thumbnail(thumb_list):
        """
        return the biggest thumbnail item
        """
        biggest = None
        big_size = 0
        for item in thumb_list:
            if biggest is None:
                biggest = item
                big_size = int(item.width) * int(item.height)
            else:
                item_size = int(item.width) * int(item.height)
                if item_size > big_size:
                    biggest = item
                    big_size = item_size
        return biggest
    
    @staticmethod
    def convert_to_python(element):
        """
        Convert to base python structures
        """
        from atom.core import XmlElement
        from atom import AtomBase
        
        ignorable_keys = ['scheme', 'namespace']
        if isinstance(element, (list, tuple)):
            output = []
            for item in element:
                output.append(YouTubeBase.convert_to_python(item))
        elif isinstance(element, dict):
            output = {}
            for key, val in element.items():
                if key.startswith("_") or key in ignorable_keys or val is None:
                    continue
                elif key == 'extension_attributes':
                    output.update(val)
                elif key == 'extension_elements':
                    for item in val:
                        # Do something with item.attributes?
                        # if item.attributes:
                        #     print item
                        #     raise
                        if item.children:
                            output[item.tag] = YouTubeBase.convert_to_python(item.children)
                        else:
                            output[item.tag] = item.text
                elif isinstance(val, (tuple, list)):
                    if len(val) == 0:
                        continue
                    output[key] = []
                    for item in val:
                        output[key].append(YouTubeBase.convert_to_python(item))
                elif isinstance(val, (basestring, int, float, bool)):
                    output[key] = val
                elif isinstance(val, dict):
                    output[key] = YouTubeBase.convert_to_python(val)
                elif issubclass(val.__class__, (XmlElement, AtomBase)):
                    output[key] = YouTubeBase.convert_to_python(val.__dict__)
                else:
                    output[key] = val
                    print "Unkonwn type: ", type(val), val.__class__
            if len(output.keys()) == 1:
                return output.values()[0]
            elif set(output.keys()) == set(('text', 'type')):
                return output['text']
            else:
                return output
        else:
            return YouTubeBase.convert_to_python(element.__dict__)


class YouTubeFeed(YouTubeBase):
    """
    A YouTube feed
    """
    def process_url(self):
        """
        Process the feed url and set the metadata and entries
        """
        if 'gdata.youtube.com' not in self.url:
            import re
            playlistid_re = re.compile("(?:user/|p=|#p/c/)([A-F0-9]{16})$")
            search = playlistid_re.search(self.url)
            if search:
                playlist_id = search.group(1)
            else:
                return
            self.url = "%s/%s" % (YOUTUBE_PLAYLIST_FEED_URI, playlist_id)
        feed = self.get_service().GetYouTubeVideoFeed(uri=self.url)
        self.metadata = self.convert_to_python(feed.__dict__)
        self.entries = self.metadata['entry'][:]
        del self.metadata['entry']


