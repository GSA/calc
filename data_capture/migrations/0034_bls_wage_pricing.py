# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-13 14:51
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0033_auto_20201211_0407'),
    ]

    operations = [
        migrations.CreateModel(
            name='bls_wage_pricing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('occ_code', models.IntegerField()),
                ('area', models.TextField(blank=True, null=True)),
                ('h_mean', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_median', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct10', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct25', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct50', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct75', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct90', models.DecimalField(decimal_places=2, max_digits=6)),
            ],
        ),
    ]
