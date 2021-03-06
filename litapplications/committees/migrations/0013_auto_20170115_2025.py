# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2017-01-15 20:25
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('committees', '0012_auto_20161017_1900'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='unit',
            options={'ordering': ['name'], 'permissions': (('appointment__can_recommend', 'Can recommend appointments to unit committees'), ('appointment__can_finalize', 'Can finalize appointments to unit committees'), ('appointment__can_see', 'Can see (but not change) appointments to unit committees'), ('email__can_send', 'Can send email for unit-specific triggers'), ('note__can_make_candidate_note', 'Can make notes on candidates for unit committees'), ('note__can_make_privileged_note', 'Can make privileged notes on candidates for unit committees'), ('note__can_see', 'Can see (but not change) notes on candidates for unit committees'), ('committee__can_create', 'Can create committees belonging to this unit')), 'verbose_name': 'Unit', 'verbose_name_plural': 'Units'},
        ),
    ]
