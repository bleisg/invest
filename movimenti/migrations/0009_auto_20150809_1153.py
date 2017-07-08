# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0008_transazione_notareg'),
    ]

    operations = [
        migrations.AlterField(
            model_name='titolo',
            name='isin',
            field=models.CharField(unique=True, max_length=15),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico1m',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=2&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico2a',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=7&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250, blank=True),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico6m',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=4&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250, blank=True),
        ),
    ]
