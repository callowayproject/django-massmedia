from django.test import TestCase
from massmedia.models import Image, ImageCustomSize


class ImageTestCase(TestCase):
    fixtures = ['test_images.json', ]

    def test_images_loaded(self):
        self.assertEqual(6, Image.objects.count())

    def test_crop(self):
        img = Image.objects.get(id=690)  # a 1400 x 933 image

        # A Vertical Crop
        ImageCustomSize.objects.create(
            image=img,
            width=700,
            height=933,
            crop_x=350,
            crop_y=0,
            crop_w=700,
            crop_h=933,
            ratio=750
        )
        # A 4:3 crop
        ImageCustomSize.objects.create(
            image=img,
            width=1200,
            height=900,
            crop_x=100,
            crop_y=0,
            crop_w=1200,
            crop_h=900,
            ratio=1333
        )
        # A mugshot crop
        ImageCustomSize.objects.create(
            image=img,
            width=100,
            height=133,
            crop_x=100,
            crop_y=100,
            crop_w=200,
            crop_h=266,
            ratio=751
        )

        # Get the vertical Crop
        expected_url = '/uploads/image/2013/06/26/neast-chambr-scholarships1_c349-0-1050-933_r200x266.jpg?fd53922e5a57e6dfe5dc9d7c6721be257b470a86'
        self.assertEqual(expected_url, img.get_200x266_url())

        # Get the 4:3 crop
        expected_url = '/uploads/image/2013/06/26/neast-chambr-scholarships1_c100-0-1300-900_r400x300.jpg?1bcd95d81b0448d29867b12ed5063df447cfab0a'
        self.assertEqual(expected_url, img.get_400x300_url())

        # Get the mugshot crop
        expected_url = '/uploads/image/2013/06/26/neast-chambr-scholarships1_c100-100-300-366_r100x133.jpg?11cbcd62163e962976d1975781f16a232c3fc3ba'
        self.assertEqual(expected_url, img.get_100x133_url())
