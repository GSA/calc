# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-05 16:33
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0027_contract_security_clearance'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='keywords',
            field=models.CharField(blank=True, db_index=True, max_length=500, null=True),
        ),
    ]
