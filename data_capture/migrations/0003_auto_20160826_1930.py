# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0002_auto_20160823_2147'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedpricelist',
            name='created_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 8, 26, 19, 30, 24, 636881, tzinfo=utc), auto_now_add=True),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submittedpricelist',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, default=datetime.datetime(2016, 8, 26, 19, 30, 28, 408909, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='submittedpricelistrow',
            name='is_muted',
            field=models.BooleanField(default=False, help_text='Whether to include this row in CALC data once its price list has been approved'),
        ),
    ]
