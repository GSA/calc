# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0014_submittedpricelist_uploaded_filename'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='escalation_rate',
            field=models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(99)], verbose_name='escalation rate (%)'),
        ),
    ]
