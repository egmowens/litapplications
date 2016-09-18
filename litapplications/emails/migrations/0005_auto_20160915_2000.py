# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-09-15 20:00
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('emails', '0004_add_units'),
    ]

    operations = [
        migrations.AlterField(
            model_name='emailtype',
            name='unit',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='committees.Unit'),
        ),
    ]