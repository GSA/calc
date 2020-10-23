# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0005_auto_20141125_0224'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='business_size',
            field=models.CharField(blank=True, max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='schedule',
            field=models.CharField(blank=True, max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='contract',
            name='sin',
            field=models.CharField(blank=True, max_length=128, null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='education_level',
            field=models.CharField(choices=[
                ('HS', 'High School'), ('AA', 'Associates'),
                ('BA', 'Bachelors'), ('MA', 'Masters'),
                ('PHD', 'Ph.D.')
            ], blank=True, max_length=5, null=True),
            preserve_default=True,
        ),
    ]
