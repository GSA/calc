# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.contrib.postgres.search import SearchVectorField


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(serialize=False,
                                        primary_key=True, verbose_name='ID',
                                        auto_created=True)),
                ('idv_piid', models.CharField(max_length=128)),
                ('piid', models.CharField(max_length=128)),
                ('vendor_name', models.CharField(max_length=128)),
                ('labor_category', models.CharField(max_length=128)),
                ('education_level', models.CharField(
                    blank=True, max_length=5, choices=[
                        ('HS', 'High School'), ('BA', 'Bachelors'),
                        ('MA', 'Masters'), ('AA', 'Associates'),
                        ('PHD', 'Ph.D.')
                    ], null=True
                )),
                ('min_years_experience', models.IntegerField()),
                ('hourly_rate_year1', models.DecimalField(
                    max_digits=5, decimal_places=2)),
                ('hourly_rate_year2', models.DecimalField(
                    blank=True, max_digits=5, null=True, decimal_places=2)),
                ('hourly_rate_year3', models.DecimalField(
                    blank=True, max_digits=5, null=True, decimal_places=2)),
                ('hourly_rate_year4', models.DecimalField(
                    blank=True, max_digits=5, null=True, decimal_places=2)),
                ('hourly_rate_year5', models.DecimalField(
                    blank=True, max_digits=5, null=True, decimal_places=2)),
                ('contractor_site', models.CharField(
                    blank=True, max_length=128, null=True)),
                ('search_index', SearchVectorField(default='', db_index=True, editable=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]
