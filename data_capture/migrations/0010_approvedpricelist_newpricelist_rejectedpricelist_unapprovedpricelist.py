# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0009_auto_20161020_1805'),
    ]

    operations = [
        migrations.CreateModel(
            name='ApprovedPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
        migrations.CreateModel(
            name='NewPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
        migrations.CreateModel(
            name='RejectedPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
        migrations.CreateModel(
            name='UnapprovedPriceList',
            fields=[
            ],
            options={
                'proxy': True,
            },
            bases=('data_capture.submittedpricelist',),
        ),
    ]
