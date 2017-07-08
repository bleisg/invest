# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0002_auto_20150723_1417'),
    ]

    operations = [
        migrations.AddField(
            model_name='titolo',
            name='storico1m_img',
            field=models.ImageField(null=True, upload_to=b'images', blank=True),
        ),
    ]
