# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('massmedia', '0002_add_contenttype_field'),
    ]

    operations = [
        migrations.CreateModel(
            name='ImageCustomSize',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('width', models.PositiveIntegerField(default=0, verbose_name='thumbnail width')),
                ('height', models.PositiveIntegerField(default=0, verbose_name='thumbnail height')),
                ('crop_x', models.PositiveIntegerField(default=0, verbose_name='crop x')),
                ('crop_y', models.PositiveIntegerField(default=0, verbose_name='crop y')),
                ('crop_w', models.PositiveIntegerField(default=0, verbose_name='crop width')),
                ('crop_h', models.PositiveIntegerField(default=0, verbose_name='crop height')),
                ('ratio', models.PositiveIntegerField(default=0, verbose_name='aspect ratio')),
                ('image', models.ForeignKey(related_name='custom_sizes', verbose_name='original image', to='massmedia.Image')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
