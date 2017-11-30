# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2017-09-18 04:18
from __future__ import unicode_literals

import django.core.files.storage
from django.db import migrations, models
import sparkle.models


class Migration(migrations.Migration):

    dependencies = [
        ('sparkle', '0012_auto_20170317_0844'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sparkleversion',
            name='file',
            field=models.FileField(null=True, storage=django.core.files.storage.FileSystemStorage(), upload_to=sparkle.models.version_upload_to),
        ),
    ]