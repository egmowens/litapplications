# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-08-22 23:00
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('candidates', '0021_candidate_starred'),
    ]

    operations = [
        migrations.AddField(
            model_name='candidate',
            name='chair_notes',
            field=models.TextField(blank=True, help_text='Any information from the chair on why the committee should particularly consider this candidate.'),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='starred',
            field=models.BooleanField(default=False, help_text='Candidates that the chair wants the committee to pay particular attention to.'),
        ),
    ]
