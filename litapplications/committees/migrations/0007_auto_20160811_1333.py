# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-11 13:33
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0006_auto_20160801_1849'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='committee',
            options={'ordering': ['long_name'], 'verbose_name': 'Committee', 'verbose_name_plural': 'Committees'},
        ),
    ]
