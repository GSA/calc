# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0002_auto_20141124_2249'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='labor_category',
            field=models.TextField(),
            preserve_default=True,
        ),
    ]
