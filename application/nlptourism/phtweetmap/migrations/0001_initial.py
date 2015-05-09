# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('tweet_id', models.IntegerField()),
                ('user', models.CharField(max_length=240)),
                ('lat', models.DecimalField(max_digits=25, decimal_places=20)),
                ('lng', models.DecimalField(max_digits=25, decimal_places=20)),
                ('text', models.CharField(max_length=240)),
                ('sentiment', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
