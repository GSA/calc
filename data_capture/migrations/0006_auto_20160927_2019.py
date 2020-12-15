# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0005_remove_submittedpricelist_contract_year'),
    ]

    operations = [
        migrations.RenameField(
            model_name='submittedpricelistrow',
            old_name='hourly_rate_year1',
            new_name='base_year_rate',
        ),
        migrations.AddField(
            model_name='submittedpricelist',
            name='escalation_rate',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99)], default=0),
            preserve_default=False,
        ),
    ]
