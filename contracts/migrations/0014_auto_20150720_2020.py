# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0013_auto_20150714_1443'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='next_year_price',
            field=models.DecimalField(
                blank=True, db_index=True, null=True, max_digits=10,
                decimal_places=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='second_year_price',
            field=models.DecimalField(
                blank=True, db_index=True, null=True, max_digits=10,
                decimal_places=2),
            preserve_default=True,
        ),
    ]
