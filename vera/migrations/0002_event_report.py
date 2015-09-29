# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import swapper


class Migration(migrations.Migration):

    dependencies = [
        ('vera', '0001_initial'),
        swapper.dependency('auth', 'User'),
        swapper.dependency('vera', 'Event'),
        swapper.dependency('vera', 'ReportStatus'),
        swapper.dependency('vera', 'Site'),
    ]

    operations = [
        migrations.CreateModel(
            name='Event',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('date', models.DateField()),
            ],
            options={
                'db_table': 'wq_event',
                'ordering': ('-date',),
                'swappable': swapper.swappable_setting('vera', 'Event'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Report',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False, auto_created=True, verbose_name='ID')),
                ('entered', models.DateTimeField(blank=True)),
                ('event', models.ForeignKey(to=swapper.get_model_name('vera', 'Event'), related_name='report_set')),
            ],
            options={
                'db_table': 'wq_report',
                'ordering': ('-entered',),
                'swappable': swapper.swappable_setting('vera', 'Report'),
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='report',
            name='status',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'ReportStatus'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='report',
            name='user',
            field=models.ForeignKey(related_name='vera_report', to=swapper.get_model_name('auth', 'User'), null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='event',
            name='site',
            field=models.ForeignKey(to=swapper.get_model_name('vera', 'Site'), null=True, blank=True, related_name='event_set'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='event',
            unique_together=set([('site', 'date')]),
        ),
    ]
