# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0011_auto_20150604_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='contract_year',
            field=models.IntegerField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
