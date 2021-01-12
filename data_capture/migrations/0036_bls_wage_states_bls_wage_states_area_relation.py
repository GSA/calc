# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-12-17 02:56
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0035_auto_20201213_1511'),
    ]

    operations = [
        migrations.CreateModel(
            name='bls_wage_states',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('state', models.CharField(max_length=500)),
                ('state_code', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='bls_wage_states_area_relation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('city', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_series_wages')),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_wage_states')),
            ],
        ),
    ]