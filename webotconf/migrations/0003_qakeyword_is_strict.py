# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-08-01 06:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webotconf', '0002_auto_20170721_1951'),
    ]

    operations = [
        migrations.AddField(
            model_name='qakeyword',
            name='is_strict',
            field=models.BooleanField(default=False, verbose_name='是否严格'),
        ),
    ]