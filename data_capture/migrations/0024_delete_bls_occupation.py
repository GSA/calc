# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-26 14:30
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0023_bls_occupation'),
    ]

    operations = [
        migrations.DeleteModel(
            name='bls_occupation',
        ),
    ]
