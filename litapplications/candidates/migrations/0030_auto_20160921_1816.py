# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-21 18:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0029_auto_20160921_1731'),
    ]

    operations = [
        migrations.AlterField(
            model_name='note',
            name='privileged',
            field=models.BooleanField(default=False, help_text='Is this note written by someone with special authority over the appointments process, like an executive director or chair'),
        ),
    ]
