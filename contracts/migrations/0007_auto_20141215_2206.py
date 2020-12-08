# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0006_auto_20141215_2203'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='sin',
            field=models.TextField(null=True, blank=True),
            preserve_default=True,
        ),
    ]
