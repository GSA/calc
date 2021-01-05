# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contracts', '0008_contract_current_price'),
    ]

    operations = [
        # create index on current_price since it is used for sort
        migrations.RunSQL(
            ' CREATE INDEX price_index ON contracts_contract '
            '("current_price"); '),
        # add GIN index on text search field
        migrations.RunSQL(
            ' CREATE INDEX search_index ON contracts_contract '
            'USING gin(search_index); '),
        # drop old index, which is a btree
        migrations.RunSQL(
            ' DROP INDEX IF EXISTS contracts_contract_a71a185f; ')
    ]
