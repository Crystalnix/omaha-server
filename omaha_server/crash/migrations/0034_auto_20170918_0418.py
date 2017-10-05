# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-18 04:18
from __future__ import unicode_literals

import crash.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crash', '0033_auto_20170814_0700'),
    ]

    operations = [
        migrations.AlterField(
            model_name='crash',
            name='archive',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=crash.models.crash_archive_upload_to),
        ),
        migrations.AlterField(
            model_name='crash',
            name='upload_file_minidump',
            field=models.FileField(blank=True, max_length=255, null=True, upload_to=crash.models.crash_upload_to),
        ),
    ]
