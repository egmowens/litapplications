# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-01 18:45
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0014_auto_20160801_1830'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='ala_id',
            field=models.CharField(max_length=15, unique=True),
        ),
    ]
