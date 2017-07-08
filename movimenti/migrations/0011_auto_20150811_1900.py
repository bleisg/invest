# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('movimenti', '0010_auto_20150809_1248'),
    ]

    operations = [
        migrations.CreateModel(
            name='posizione',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('opened', models.BooleanField(default=True)),
            ],
        ),
        migrations.AlterModelOptions(
            name='quota',
            options={'ordering': ['data'], 'verbose_name_plural': 'Quote di capitale'},
        ),
        migrations.AlterField(
            model_name='investimento',
            name='descr',
            field=models.TextField(verbose_name=b'Descrizione', blank=True),
        ),
        migrations.AlterField(
            model_name='investimento',
            name='nome',
            field=models.CharField(max_length=30),
        ),
        migrations.AlterField(
            model_name='quota',
            name='quantita',
            field=models.DecimalField(verbose_name=b'Quantit\xc3\xa0', max_digits=10, decimal_places=5),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='descr',
            field=models.CharField(max_length=100, verbose_name=b'Descrizione', blank=True),
        ),
        migrations.AlterField(
            model_name='titolo',
            name='id_tipo',
            field=models.ForeignKey(verbose_name=b'Tipologia', to='movimenti.tipo'),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='costo',
            field=models.DecimalField(help_text=b'Importo sempre positivo. Nello scarico indicare un importo negativo per compensazione', null=True, max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='costounitario',
            field=models.DecimalField(null=True, verbose_name=b'Costo unitario', max_digits=15, decimal_places=9, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='imposta_dietimi',
            field=models.DecimalField(null=True, verbose_name=b'Imposta sui dietimi', max_digits=10, decimal_places=5, blank=True),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='invest',
            field=models.ForeignKey(verbose_name=b'Investimento', to='movimenti.investimento'),
        ),
        migrations.AlterField(
            model_name='transazione',
            name='quantity',
            field=models.IntegerField(null=True, verbose_name=b'Quantit\xc3\xa0', blank=True),
        ),
        migrations.AddField(
            model_name='posizione',
            name='titolo',
            field=models.ForeignKey(to='movimenti.titolo'),
        ),
        migrations.AddField(
            model_name='transazione',
            name='posizione',
            field=models.ForeignKey(to='movimenti.posizione', null=True),
        ),
    ]
