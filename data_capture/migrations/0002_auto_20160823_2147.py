# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='contract_end',
            field=models.DateField(null=True, blank=True),
        ),
        migrations.AlterField(
            model_name='submittedpricelist',
            name='contract_start',
            field=models.DateField(null=True, blank=True),
        ),
    ]
