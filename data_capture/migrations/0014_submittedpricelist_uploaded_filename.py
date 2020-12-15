# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0013_auto_20161214_1517'),
    ]

    operations = [
        migrations.AddField(
            model_name='submittedpricelist',
            name='uploaded_filename',
            field=models.CharField(default='unnamed', max_length=128, help_text="Name of the file that was uploaded, as it was called on the uploader's system. For display purposes only."),
            preserve_default=False,
        ),
    ]
