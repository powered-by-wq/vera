from __future__ import unicode_literals
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        ('vera', '0001_initial'),
    ]
    operations = [
        migrations.CreateModel(
            name='Site',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, db_index=True, max_length=255)),
                ('slug', models.CharField(blank=True, max_length=255)),
            ],
            options={
                'abstract': False,
            },
        ),
    ]
