# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0006_auto_20160927_2019'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedpricelistrow',
            name='current_price',
        ),
    ]
