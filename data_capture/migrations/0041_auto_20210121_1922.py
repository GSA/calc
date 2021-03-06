# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2021-01-21 19:22
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0040_auto_20210114_0308'),
    ]

    operations = [
        migrations.CreateModel(
            name='bls_base_year_increment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('avg_rate_inc', models.DecimalField(decimal_places=1, max_digits=6)),
            ],
        ),
        migrations.CreateModel(
            name='bls_data',
            fields=[
                ('series_id', models.CharField(max_length=300, primary_key=True, serialize=False)),
                ('series_title', models.CharField(max_length=2000)),
                ('area_code', models.CharField(max_length=100)),
                ('area_level', models.CharField(max_length=100)),
                ('area_text', models.CharField(max_length=100)),
                ('occupation_code', models.CharField(max_length=100)),
                ('occupation_text', models.CharField(max_length=300)),
                ('job_char_code', models.CharField(max_length=100)),
                ('job_char_text', models.CharField(max_length=2000)),
                ('work_level_code', models.CharField(max_length=100)),
                ('work_level_text', models.CharField(max_length=300)),
                ('average_hourly_wage', models.CharField(max_length=100)),
                ('relative_std_error', models.CharField(max_length=20)),
                ('average_hourly_wage_footnote', models.CharField(max_length=100)),
                ('relative_std_error_footnote', models.CharField(max_length=100)),
            ],
        ),
        migrations.CreateModel(
            name='bls_lcat',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('lcat_title', models.CharField(max_length=200)),
            ],
        ),
        migrations.CreateModel(
            name='bls_occs',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('occupation_code', models.IntegerField()),
                ('occupation', models.CharField(max_length=500)),
            ],
        ),
        migrations.CreateModel(
            name='bls_occupation_lcat_mapping',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('occupation_code', models.CharField(max_length=100)),
                ('lcat', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_lcat')),
            ],
        ),
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
            ],
        ),
        migrations.CreateModel(
            name='bls_state_city_mapping',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('city', models.CharField(max_length=200)),
                ('state', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_state')),
            ],
        ),
        migrations.AddField(
            model_name='bls_pricing',
            name='area_code',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_state_city_mapping'),
        ),
        migrations.AddField(
            model_name='bls_pricing',
            name='lcat_id',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='data_capture.bls_lcat'),
        ),
    ]
