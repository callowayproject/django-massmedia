import unittest
from massmedia.models import Collection,CollectionRelation
from django.contrib.sites.models import Site
from django.conf import settings
from django.template import Template,Context
import os
import shutil

expected_metadata = [{'album': 'Verve Remixed 4',
  'author': 'Marlena Shaw',
  'bit_rate': '320000',
  'bits_per_sample': '16',
  'comment': ['iTunPGAP: 0',
               'iTunNORM: 00001077 00001076 0000B9A6 0000BEBB 00005343 00005343 00008823 00008983 00019AB6 00016CB1',
               'iTunSMPB: 00000000 00000210 00000ABC 0000000000A7A9B4 00000000 0097FE35 00000000 00000000 00000000 00000000 00000000 00000000',
               'iTunes_CDDB_1: BE0B0F0C+212541+12+150+12556+26998+51604+70291+86197+103429+124804+136961+161945+174554+192931',
               'iTunes_CDDB_TrackNumber: 4'],
  'compr_rate': '4.41',
  'duration': '0:04:09.234300',
  'endian': 'Big ',
  'format_version': 'MPEG version 1 layer III',
  'mime_type': 'audio/mpeg',
  'nb_channel': '2',
  'producer': 'iTunes v7.6',
  'sample_rate': '44100',
  'title': 'California Soul (Diplo/ Mad Decent Remix)',
  'track_number': '4',
  'track_total': '12'},
 {'bits_per_pixel': '24',
  'comment': 'JPEG quality: 75%',
  'compr_rate': '18.9018237306',
  'compression': 'JPEG (Baseline)',
  'endian': 'Big ',
  'format_version': 'JFIF 1.01',
  'height': '800',
  'height_dpi': '96',
  'mime_type': 'image/jpeg',
  'pixel_format': 'YCbCr',
  'width': '1280',
  'width_dpi': '96'},
 {},
 {'album': 'Snatch Soundtrack',
  'author': 'Klint',
  'bit_rate': '128000',
  'bits_per_sample': '16',
  'comment': 'iTunNORM: 00000294 000002C7 00001438 0000159B 0002BF37 0002BF37 00007300 00007305 00013897 00013897',
  'compr_rate': '11.025',
  'duration': '0:03:31.043250',
  'endian': 'Big ',
  'format_version': 'MPEG version 1 layer III',
  'mime_type': 'audio/mpeg',
  'music_genre': 'Drum & Bass',
  'nb_channel': '2',
  'sample_rate': '44100',
  'title': 'Diamond'},
 {},
 {'comment': ['Play speed: 100.0%', 'User volume: 100.0%'],
  'creation_date': '2008-07-17 15:09:23',
  'duration': '0:09:33.881179',
  'endian': 'Big ',
  'last_modification': '2008-07-17 15:10:13',
  'mime_type': 'video/mp4'},
 {'bits_per_pixel': '24',
  'compr_rate': '13.8163954559',
  'compression': 'deflate',
  'endian': 'Big ',
  'height': '150',
  'mime_type': 'image/png',
  'pixel_format': 'RGB',
  'width': '300'},
 {'bit_rate': '346450.713212',
  'bits_per_sample': '16',
  'compression': ['Sorensen H.263',
                   'MPEG-2 layer III, 64.0 Kbit/sec, 22.1 kHz'],
  'duration': '0:00:21.943000',
  'endian': 'Big ',
  'format_version': 'Macromedia Flash video version 1',
  'mime_type': 'video/x-flv',
  'nb_channel': '1',
  'producer': ['YouTube, Inc.', 'YouTube Metadata Injector.'],
  'sample_rate': '22050'}]

expected_widgets = """<a href="/media/audio/2009/Jan/14/04_California_Soul_Diplo__Mad_Decent_Remix.mp3">04 California Soul (Diplo_ Mad Decent Remix)</a><embed width="None" height="None" name="plugin" src="/media/audio/2009/Jan/14/04_California_Soul_Diplo__Mad_Decent_Remix.mp3" type="audio/mpeg"/><a href="/media/img/2009/Jan/14/acrobat.jpg">acrobat</a><img src="/media/img/2009/Jan/14/acrobat.jpg" height="800" width="1280"/><a href="/media/video/2009/Jan/14/centaur_1.mpg">centaur_1</a><embed width="None" height="None" name="plugin" src="/media/video/2009/Jan/14/centaur_1.mpg" type="video/mpeg"/><a href="/media/audio/2009/Jan/14/Diamond.mp3">Diamond</a><embed width="None" height="None" name="plugin" src="/media/audio/2009/Jan/14/Diamond.mp3" type="audio/mpeg"/><a href="/media/flash/2009/Jan/14/flashegg2.swf">flashegg2</a><object width="None" height="None"><param name="movie" value="/media/flash/2009/Jan/14/flashegg2.swf"><embed src="/media/flash/2009/Jan/14/flashegg2.swf" width="None" height="None"></embed></object><a href="/media/audio/2009/Jan/14/gsai.m4a">gsai</a><embed width="None" height="None" name="plugin" src="/media/audio/2009/Jan/14/gsai.m4a" type="audio/mp4a-latm"/><a href="/media/img/2009/Jan/14/overlay.png">overlay</a><img src="/media/img/2009/Jan/14/overlay.png" height="150" width="300"/><a href="/media/video/2009/Jan/14/xCciDlngWDc.flv">xCciDlngWDc</a><div id="container"><a href="http://www.macromedia.com/go/getflashplayer">Get the Flash Player</a> to see this player.</div><script type="text/javascript" src="/media/swfobject.js"></script><script type="text/javascript">
	var s1 = new SWFObject("/media/player.swf","ply","","","9","#FFFFFF");
	s1.addParam("allowfullscreen","true");
	s1.addParam("allowscriptaccess","always");
	s1.addParam("flashvars","file=/media/video/2009/Jan/14/xCciDlngWDc.flv&image=");
	s1.write("container");
</script>"""

class CollectionTestCase(unittest.TestCase):
    def setUp(self):
        shutil.copy(
            os.path.join(settings.MEDIA_ROOT,'Archive.zip.test'),
            os.path.join(settings.MEDIA_ROOT,'Archive.zip')
        )
        site = Site.objects.create(domain='example.com',name='Example')
        self.collection = Collection.objects.create(title='test',slug='test',zip_file='Archive.zip')
        self.collection.sites.add(site)

    def testCollection(self):
        relations = CollectionRelation.objects.filter(collection=self.collection)
        self.assertEqual(len(relations), 8 ,\
            'Wrong number of files collected: %s != 8'%len(relations))
    
        self.assertEqual(expected_metadata,
            [dict(x.content_object.metadata) for x in relations],
            'Wrong metadata info')
        return
        testplate =  Template("""
            {% load media_widgets %}
            {% spaceless %}
            {% for related in relations %}
                <a href="{{ related.content_object.get_absolute_url }}">{{ related.content_object }}</a>
                {% show_media related.content_object %}
            {% endfor %}
            {% endspaceless %}""")
        self.assertEqual(expected_widgets, testplate.render(Context({'relations':relations})).strip())
