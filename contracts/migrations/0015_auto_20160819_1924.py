# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('contracts', '0014_auto_20150720_2020'),
    ]

    operations = [
        migrations.CreateModel(
            name='BulkUploadContractSource',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, serialize=False, primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('has_been_loaded', models.BooleanField(default=False)),
                ('original_file', models.BinaryField()),
                ('procurement_center', models.CharField(db_index=True, choices=[('R10', 'Region 10')], max_length=5)),
                ('submitter', models.ForeignKey(null=True, blank=True, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='contract',
            name='upload_source',
            field=models.ForeignKey(null=True, blank=True, to='contracts.BulkUploadContractSource'),
        ),
    ]
