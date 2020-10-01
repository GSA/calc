# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.utils.timezone import utc
import datetime
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('data_capture', '0010_approvedpricelist_newpricelist_rejectedpricelist_unapprovedpricelist'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submittedpricelist',
            name='status_changed_at',
            field=models.DateTimeField(default=datetime.datetime(2016, 11, 3, 21, 7, 54, 498309, tzinfo=utc)),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='submittedpricelist',
            name='status_changed_by',
            field=models.ForeignKey(default=1, related_name='+', to=settings.AUTH_USER_MODEL, on_delete='DO_NOTHING'),
            preserve_default=False,
        ),
    ]
