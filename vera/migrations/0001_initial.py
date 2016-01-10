# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swapper


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Parameter',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, unique=True, max_length=255)),
                ('is_numeric', models.BooleanField(default=False)),
                ('units', models.CharField(null=True, max_length=50, blank=True)),
            ],
            options={
                'db_table': 'wq_parameter',
                'ordering': ('name',),
                'swappable': swapper.swappable_setting('vera', 'Parameter'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ReportStatus',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=255)),
                ('is_valid', models.BooleanField(default=False)),
            ],
            options={
                'db_table': 'wq_reportstatus',
                'verbose_name_plural': 'report statuses',
                'swappable': swapper.swappable_setting('vera', 'ReportStatus'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('latitude', models.FloatField(null=True, blank=True)),
                ('longitude', models.FloatField(null=True, blank=True)),
            ],
            options={
                'db_table': 'wq_site',
                'swappable': swapper.swappable_setting('vera', 'Site'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='site',
            unique_together=set([('latitude', 'longitude')]),
        ),
        migrations.AlterUniqueTogether(
            name='reportstatus',
            unique_together=set([('slug',)]),
        ),
    ]
