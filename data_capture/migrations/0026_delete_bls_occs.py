# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-26 14:34
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0025_bls_occs'),
    ]

    operations = [
        migrations.DeleteModel(
            name='bls_occs',
        ),
    ]
