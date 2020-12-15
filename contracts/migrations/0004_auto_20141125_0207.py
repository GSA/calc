# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0003_auto_20141124_2256'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contract_end',
            field=models.DateField(default='1979-01-01'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='contract',
            name='contract_start',
            field=models.DateField(default='1979-01-01'),
            preserve_default=False,
        ),
    ]
