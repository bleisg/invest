# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0009_auto_20150809_1153'),
    ]

    operations = [
        migrations.AlterField(
            model_name='transazione',
            name='costounitario',
            field=models.DecimalField(null=True, max_digits=10, decimal_places=7, blank=True),
        ),
    ]
