# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0012_auto_20150618_1704'),
    ]

    operations = [
        migrations.AlterField(
            model_name='contract',
            name='business_size',
            field=models.CharField(blank=True, null=True,
                                   db_index=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='contractor_site',
            field=models.CharField(blank=True, null=True,
                                   db_index=True, max_length=128),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='current_price',
            field=models.DecimalField(
                max_digits=10, blank=True, null=True, db_index=True,
                decimal_places=2),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='education_level',
            field=models.CharField(
                db_index=True, blank=True, null=True,
                choices=[
                    ('HS', 'High School'), ('AA', 'Associates'),
                    ('BA', 'Bachelors'), ('MA', 'Masters'),
                    ('PHD', 'Ph.D.')
                ], max_length=5
            ),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='labor_category',
            field=models.TextField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='min_years_experience',
            field=models.IntegerField(db_index=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='contract',
            name='schedule',
            field=models.CharField(blank=True, null=True,
                                   db_index=True, max_length=128),
            preserve_default=True,
        ),
    ]
