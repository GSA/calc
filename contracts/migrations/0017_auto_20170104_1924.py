# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0016_bulkuploadcontractsource_file_mime_type'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bulkuploadcontractsource',
            name='procurement_center',
            field=models.CharField(choices=[('R10', 'Region 10'), ('S70', 'Schedule 70')], db_index=True, max_length=5),
        ),
    ]
