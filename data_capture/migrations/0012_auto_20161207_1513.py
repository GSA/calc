# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0011_auto_20161103_2108'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='contract_number',
            field=models.CharField(help_text='List the full contract number, e.g. GSXXXXXXX or 47XXXXXXXXXXX.', validators=[django.core.validators.RegexValidator(regex='^[a-zA-Z0-9-_]+$', message='Please use only letters, numbers, and dashes (-).')], max_length=128),
        ),
    ]
