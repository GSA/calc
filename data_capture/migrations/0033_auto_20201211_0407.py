# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-11 04:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0032_auto_20201210_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='bls_series_wages',
            name='city',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='bls_series_wages',
            name='occupation_title',
            field=models.TextField(blank=True, null=True),
        ),
    ]
