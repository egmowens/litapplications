# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-06-04 15:31
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0036_auto_20170410_0025'),
    ]

    operations = [
        migrations.AddField(
            model_name='appointment',
            name='year_end',
            field=models.IntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='appointment',
            name='year_start',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]
