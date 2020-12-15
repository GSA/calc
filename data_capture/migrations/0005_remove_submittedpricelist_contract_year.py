# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0004_auto_20160922_1539'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedpricelist',
            name='contract_year',
        ),
    ]
