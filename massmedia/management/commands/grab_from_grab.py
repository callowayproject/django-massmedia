from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand, CommandError
from django.template.defaultfilters import slugify
from django.contrib.sites.models import Site
from massmedia.models import GrabVideo,Image

import urllib2
import urllib
from lxml import etree
from datetime import datetime
from base64 import b64encode
import os
from optparse import make_option
import sha

class Command(BaseCommand):
     option_list = BaseCommand.option_list + (
          make_option('-l', '--layout', dest='layout', default='851501',
             help='Grab layout id of the player to use (defaults to twt standard)'
          ),
     )     
     def handle(self, *a, **kw):
          asset_id = None
          if len(a):
               asset_id = a[0]
          
          try:
               from massmedia.settings import GRAB_API_URL,GRAB_API_KEY
               assert GRAB_API_KEY and GRAB_API_URL
          except (ImportError, AssertionError):
               raise CommandError('You must define your Grab networks settings!')
          
          if asset_id:
               GRAB_API_URL = '%s%s' % (GRAB_API_URL, asset_id)
          
          req = urllib2.Request(GRAB_API_URL, None, {
               'Authorization': 'Basic %s' % b64encode('%s:' % GRAB_API_KEY)
          })
          try:
               response = urllib2.urlopen(req)
          except urllib2.HTTPError, e:
               raise CommandError('Grab networks had a problem request: %s' % e)
          except urllib2.URLError, e:
               raise CommandError('Failed to reach Grab networks: %s' % e)

          parser = etree.XMLParser()
          parser.feed(response.read().decode('latin1').encode('utf8'))
          for element in parser.close().iter("*"):
               if element.tag == 'video':
                    d = {}
                    for e in element.getchildren():
                         if e.tag == 'categories':
                              d[e.tag] = map(lambda x: unicode(x.text.strip())[:50], e.getchildren())
                         elif e.tag == 'id':
                              d['id'] = 'V%s' % e.text
                         else:
                              d[e.tag] = e.text
                    
                    title = d['title'] 
                    time = datetime.strptime(d['created-at'],'%Y-%m-%dT%H:%M:%SZ')
                    slug,s = sha.new(title).hexdigest(),sha.new(time.strftime("%d-%b-%Y %H:%M:%S").lower() + title).hexdigest()
                    try:
                         video = GrabVideo.objects.get(title=title,slug=slug,creation_date=time)
                         continue
                    except GrabVideo.DoesNotExist:
                         try:
                              thumb,_ = Image.objects.get_or_create(slug=s)
                         
                              thumb.file.save(os.path.basename(d['preview-url']),
                                   ContentFile(urllib.urlopen(d['preview-url']).read()))
                              
                              if not ',' in unicode(d['keywords'] or ''):
                                   d['keywords'] = map(lambda x: unicode(x.strip())[:50], unicode(d['keywords'] or '').split())
                              else:
                                   d['keywords'] = map(lambda x: unicode(x.strip())[:50], unicode(d['keywords'] or '').split(','))
                              video,_ = GrabVideo.objects.get_or_create(
                                   title = title,
                                   slug = slug,
                                   creation_date = time,
                                   one_off_author = d['provider-name'],
                                   credit = unicode(d['copyright'] or '')[:150],
                                   caption = unicode(d['summary'] or '')[:255],
                                   asset_id = d['id'],
                                   layout_id = kw.get('layout'),
                                   thumbnail = thumb,
                                   categories = ','.join(d['categories'])[:255],
                                   keywords = ','.join(d['keywords'])[:255]
                              )
                              video.sites.add(Site.objects.get_current())
                         except:
                              continue