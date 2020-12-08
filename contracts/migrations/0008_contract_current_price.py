# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0007_auto_20141215_2206'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='current_price',
            field=models.DecimalField(
                max_digits=10, null=True, blank=True, decimal_places=2),
            preserve_default=True,
        ),
    ]
