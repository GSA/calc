# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-23 02:58
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0037_bls_wage_year_addition_price'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bls_wage_year_addition_price',
            name='price',
            field=models.DecimalField(decimal_places=6, max_digits=8),
        ),
    ]
