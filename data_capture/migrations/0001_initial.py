# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0014_auto_20150720_2020'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='SubmittedPriceList',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('contract_number', models.CharField(help_text='List the full contract number, e.g. GSXXXXXXX or 47XXXXXXXXXXX.', max_length=128)),
                ('vendor_name', models.CharField(max_length=128)),
                ('is_small_business', models.BooleanField()),
                ('schedule', models.CharField(max_length=128)),
                ('contractor_site', models.CharField(verbose_name='Worksite', choices=[('Customer', 'Customer'), ('Contractor', 'Contractor'), ('Both', 'Both')], max_length=128)),
                ('contract_year', models.IntegerField(null=True, blank=True)),
                ('contract_start', models.DateField(help_text='Use MM/DD/YY format, e.g. "10/25/06".', null=True, blank=True)),
                ('contract_end', models.DateField(help_text='Use MM/DD/YY format, e.g. "10/25/06".', null=True, blank=True)),
                ('is_approved', models.BooleanField(default=False)),
                ('serialized_gleaned_data', models.TextField(help_text='The JSON-serialized data from the upload, including information about any rows that failed validation.')),
                ('submitter', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=models.CASCADE)),
            ],
        ),
        migrations.CreateModel(
            name='SubmittedPriceListRow',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('labor_category', models.TextField()),
                ('education_level', models.CharField(null=True, choices=[('HS', 'High School'), ('AA', 'Associates'), ('BA', 'Bachelors'), ('MA', 'Masters'), ('PHD', 'Ph.D.')], max_length=5, blank=True)),
                ('min_years_experience', models.IntegerField()),
                ('hourly_rate_year1', models.DecimalField(max_digits=10, decimal_places=2)),
                ('current_price', models.DecimalField(max_digits=10, null=True, decimal_places=2, blank=True)),
                ('sin', models.TextField(null=True, blank=True)),
                ('contract_model', models.OneToOneField(null=True, blank=True, to='contracts.Contract', on_delete=django.db.models.deletion.SET_NULL)),
                ('price_list', models.ForeignKey(to='data_capture.SubmittedPriceList', related_name='rows')),
            ],
        ),
    ]
