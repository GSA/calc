# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-10-26 14:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0027_bls_occs'),
    ]

    operations = [
        migrations.CreateModel(
            name='bls_pricing',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('occ_code', models.IntegerField()),
                ('h_mean', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_median', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct10', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct25', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct50', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct75', models.DecimalField(decimal_places=2, max_digits=6)),
                ('h_pct90', models.DecimalField(decimal_places=2, max_digits=6)),
                ('area_code', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_state_city_mapping')),
                ('lcat_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_lcat')),
            ],
        ),
    ]
