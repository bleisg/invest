# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='tipo',
            options={'ordering': ['nome'], 'verbose_name_plural': 'Tipologia dei titoli'},
        ),
        migrations.AlterModelOptions(
            name='tipo_transazione',
            options={'verbose_name_plural': 'Tipo transazione'},
        ),
        migrations.AddField(
            model_name='quota',
            name='data',
            field=models.DateField(default=datetime.date.today, verbose_name=b'Date'),
        ),
        migrations.AddField(
            model_name='quota',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AddField(
            model_name='titolo',
            name='note',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='investimento',
            name='descr',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='tipo',
            name='descrizione',
            field=models.TextField(blank=True),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='descr',
            field=models.CharField(max_length=100, blank=True),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='emittente',
            field=models.CharField(default=b'idem', max_length=30),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico1m',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=2&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico2a',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=7&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='storico6m',
            field=models.URLField(default=b'http://it.advfn.com/p.php?pid=staticchart&s=BIT%5EIES&t=37&p=4&dm=0&vol=0&width=280&height=200&min_pre=0&min_after=0', max_length=250),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='tag',
            field=models.CharField(max_length=30, blank=True),
        ),
    ]
