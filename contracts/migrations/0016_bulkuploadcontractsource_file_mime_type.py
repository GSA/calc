# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0015_auto_20160819_1924'),
    ]

    operations = [
        migrations.AddField(
            model_name='bulkuploadcontractsource',
            name='file_mime_type',
            field=models.TextField(default='text/csv'),
            preserve_default=False,
        ),
    ]
