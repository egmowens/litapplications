# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-02 18:02
from __future__ import unicode_literals

from django.db import migrations
import django.db.models.manager


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0015_auto_20160801_1845'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='candidate',
            options={'ordering': ['first_name', 'last_name'], 'verbose_name': 'Candidate', 'verbose_name_plural': 'Candidates'},
        ),
        migrations.AlterModelManagers(
            name='candidate',
            managers=[
                ('even_obsolete', django.db.models.manager.Manager()),
            ],
        ),
    ]
