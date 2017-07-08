# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import datetime


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='investimento',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=20)),
                ('descr', models.TextField()),
            ],
            options={
                'verbose_name_plural': 'Investimenti',
            },
        ),
        migrations.CreateModel(
            name='quota',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=30)),
                ('tipo', models.CharField(default=b'DEP', max_length=3, choices=[(b'DEP', b'Deposito cash'), (b'PRE', b'Prelievo cash')])),
                ('quantita', models.DecimalField(max_digits=10, decimal_places=5)),
            ],
        ),
        migrations.CreateModel(
            name='tipo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=20)),
                ('descrizione', models.TextField()),
                ('tassazione', models.DecimalField(max_digits=5, decimal_places=2)),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name_plural': 'Tipologia',
            },
        ),
        migrations.CreateModel(
            name='tipo_transazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
            ],
            options={
                'verbose_name_plural': 'Tipologia_Transazione',
            },
        ),
        migrations.CreateModel(
            name='titolo',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('nome', models.CharField(max_length=50)),
                ('sigla', models.CharField(max_length=50)),
                ('descr', models.CharField(max_length=100)),
                ('emittente', models.CharField(max_length=30)),
                ('mercato', models.CharField(max_length=30)),
                ('isin', models.CharField(max_length=15)),
                ('dividendo', models.BooleanField()),
                ('storico1m', models.URLField(max_length=250)),
                ('storico6m', models.URLField(max_length=250)),
                ('storico2a', models.URLField(max_length=250)),
                ('id_tipo', models.ForeignKey(to='movimenti.tipo')),
            ],
            options={
                'ordering': ['nome'],
                'verbose_name_plural': 'Titoli',
            },
        ),
        migrations.CreateModel(
            name='transazione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', models.DateField(default=datetime.date.today, verbose_name=b'Date')),
                ('quantity', models.IntegerField()),
                ('costounitario', models.DecimalField(max_digits=10, decimal_places=5)),
                ('costo', models.DecimalField(max_digits=10, decimal_places=5)),
                ('tag', models.CharField(max_length=30)),
                ('invest', models.ForeignKey(to='movimenti.investimento')),
                ('tipo', models.ForeignKey(to='movimenti.tipo_transazione')),
                ('titolo', models.ForeignKey(to='movimenti.titolo')),
            ],
            options={
                'ordering': ['data'],
                'verbose_name_plural': 'Transazioni',
            },
        ),
    ]
