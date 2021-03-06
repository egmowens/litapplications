# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-31 00:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='committee',
            name='long_name',
            field=models.CharField(blank=True, max_length=50),
        ),
        migrations.AddField(
            model_name='committee',
            name='max_appointees',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='committee',
            name='min_appointees',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='committee',
            name='short_code',
            field=models.CharField(blank=True, max_length=15),
        ),
    ]
