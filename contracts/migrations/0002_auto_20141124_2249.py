# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='hourly_rate_year1',
            field=models.DecimalField(max_digits=10, decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='hourly_rate_year2',
            field=models.DecimalField(
                decimal_places=2, null=True, blank=True, max_digits=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='hourly_rate_year3',
            field=models.DecimalField(
                decimal_places=2, null=True, blank=True, max_digits=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='hourly_rate_year4',
            field=models.DecimalField(
                decimal_places=2, null=True, blank=True, max_digits=10),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='hourly_rate_year5',
            field=models.DecimalField(
                decimal_places=2, null=True, blank=True, max_digits=10),
            preserve_default=True,
        ),
    ]
