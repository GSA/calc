# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0012_auto_20161207_1513'),
    ]

    operations = [
        migrations.DeleteModel(
            name='NewPriceList',
        ),
        migrations.DeleteModel(
            name='UnapprovedPriceList',
        ),
        migrations.CreateModel(
            name='RetiredPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
        migrations.CreateModel(
            name='UnreviewedPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
        migrations.AlterField(
            model_name='submittedpricelist',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'unreviewed'), (1, 'approved'), (2, 'retired'), (3, 'rejected')]),
        ),
    ]
