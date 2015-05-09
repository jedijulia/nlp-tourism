# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('phtweetmap', '0002_tweet_retrieved'),
    ]

    operations = [
        migrations.AddField(
            model_name='tweet',
            name='actual_classification',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tweet',
            name='classification',
            field=models.CharField(max_length=20, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='tweet',
            name='classified',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='tweet',
            name='sentiment',
            field=models.CharField(max_length=100, null=True, blank=True),
        ),
    ]
