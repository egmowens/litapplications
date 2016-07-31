# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-30 21:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='review_complete',
            field=models.BooleanField(default=False, help_text='Have recommendations been finalized?'),
        ),
    ]