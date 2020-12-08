# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0003_auto_20160826_1930'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='contractor_site',
            field=models.CharField(choices=[('Customer', 'Customer/Offsite'), ('Contractor', 'Contractor/Onsite'), ('Both', 'Both')], max_length=128, verbose_name='Worksite'),
        ),
    ]
