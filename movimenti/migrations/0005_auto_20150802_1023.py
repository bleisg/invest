# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0004_auto_20150801_2231'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transazione',
            name='costo',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='costounitario',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='quantity',
            field=models.IntegerField(null=True, blank=True),
        ),
    ]
