# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0003_titolo_storico1m_img'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='titolo',
            name='storico1m_img',
        ),
        migrations.AddField(
            model_name='transazione',
            name='imposta',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AddField(
            model_name='transazione',
            name='rateo',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='costo',
            field=models.DecimalField(max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='costounitario',
            field=models.DecimalField(max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='quantity',
            field=models.IntegerField(blank=True),
        ),
    ]
