# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0006_transazione_imposta_dietimi'),
    ]

    operations = [
        migrations.AddField(
            model_name='transazione',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='transazione',
            name='nreg',
            field=models.CharField(max_length=40, blank=True),
        ),
    ]
