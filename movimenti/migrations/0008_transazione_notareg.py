# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0007_auto_20150802_1503'),
    ]

    operations = [
        migrations.AddField(
            model_name='transazione',
            name='notareg',
            field=models.CharField(max_length=40, blank=True),
        ),
    ]
