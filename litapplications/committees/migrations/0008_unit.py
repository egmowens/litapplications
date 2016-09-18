# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-15 19:41
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0007_auto_20160811_1333'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=20)),
            ],
            options={
                'ordering': ['name'],
                'verbose_name': 'Unit',
                'verbose_name_plural': 'Units',
            },
        ),
    ]