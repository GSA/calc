# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0009_update_price_search_index'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='contract_year',
            field=models.DecimalField(
                null=True, max_digits=1, decimal_places=0, blank=True),
            preserve_default=True,
        ),
    ]
