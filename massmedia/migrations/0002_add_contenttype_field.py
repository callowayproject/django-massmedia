# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('massmedia', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='embed',
            name='content_type',
            field=models.CharField(choices=[(b'audio', b'Audio'), (b'document', b'Document'), (b'interactive', b'Interactive'), (b'presentation', b'Presentation'), (b'video', b'Video')], max_length=50, blank=True, help_text='The type of content this contains. For display purposes.', null=True, verbose_name='Content Type'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='flash',
            name='content_type',
            field=models.CharField(choices=[(b'audio', b'Audio'), (b'document', b'Document'), (b'interactive', b'Interactive'), (b'presentation', b'Presentation'), (b'video', b'Video')], max_length=50, blank=True, help_text='The type of content this contains. For display purposes.', null=True, verbose_name='Content Type'),
            preserve_default=True,
        ),
    ]
