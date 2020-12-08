# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('data_capture', '0007_remove_submittedpricelistrow_current_price'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='submittedpricelist',
            name='is_approved',
        ),
        migrations.AddField(
            model_name='submittedpricelist',
            name='status',
            field=models.IntegerField(default=0, choices=[(0, 'new'), (1, 'approved'), (2, 'unapproved')]),
        ),
        migrations.AddField(
            model_name='submittedpricelist',
            name='status_changed_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.AddField(
            model_name='submittedpricelist',
            name='status_changed_by',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL, null=True, related_name='+'),
        ),
    ]
