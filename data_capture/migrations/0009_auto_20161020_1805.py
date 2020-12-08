# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0008_auto_20161019_1853'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='status',
            field=models.IntegerField(choices=[(0, 'new'), (1, 'approved'), (2, 'unapproved'), (3, 'rejected')], default=0),
        ),
    ]
