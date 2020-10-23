from django.db.models import Count, Sum, Q

from contracts.models import Contract
from .base import BaseMetric


# Sometimes we want to dynamically build a Q object by starting
# with a "null query" that has nothing in it, and then adding
# more Q objects via the OR operator (i.e., "|").
#
# This particular null query has the advantage that no database query
# is executed if nothing is OR'd with it. It was taken from
# https://stackoverflow.com/a/46225056.
NULL_QUERY = Q(pk__in=[])


class Metric(BaseMetric):
    '''
    Measures the number of duplicate Contract entries in the database.

    By "duplicate" we mean that the entries have the same core fields
    but differ along other axes.

    This code is based on the following experimental PR:

        https://github.com/18F/calc/pull/1029
    '''

    CORE_FIELDS = [
        'vendor_name',
        'labor_category',
        'idv_piid',
        'current_price',
    ]

    CORE_FIELD_NAMES = [
        Contract._meta.get_field(field).verbose_name
        for field in CORE_FIELDS
    ]

    def _get_dupe_info(self):
        '''
        Return a queryset where each entry contains information
        about a specific type of duplicate: its core field
        values and its count (i.e., the number of Contract models
        that match its core fields).
        '''

        return Contract.objects.values(*self.CORE_FIELDS)\
            .annotate(count=Count(self.CORE_FIELDS[0]))\
            .filter(count__gt=1)\
            .distinct()

    def get_examples_queryset(self):
        total = 0
        dupes = NULL_QUERY

        # There might be a way to do this all with one database
        # query, but since we don't expect this report to
        # be executed often, and since we only need MAX_EXAMPLES
        # examples, it's not a big deal.
        for dupeinfo in self._get_dupe_info():
            # Find all the records that share the same core fields
            # and add them to our set of duplicates.
            dupes = dupes | Q(**{
                field: dupeinfo[field] for field in self.CORE_FIELDS
            })

            total += dupeinfo['count']
            if total > self.MAX_EXAMPLES:
                break

        # We want to order the results by our core fields so it's
        # easier to visually group them together and see what the
        # differences between them (if any) are.
        return Contract.objects.filter(dupes)\
            .order_by(*self.CORE_FIELDS)[:self.MAX_EXAMPLES]

    def count(self) -> int:
        return self._get_dupe_info()\
            .aggregate(Sum('count'))['count__sum'] or 0

    desc = f'''
    labor rates appear to be duplicates.
    '''

    footnote = f'''
    By "duplicates" we mean that they share the same values
    for {', '.join(CORE_FIELD_NAMES[:-1])} and {CORE_FIELD_NAMES[-1]}.
    They may (and likely do) vary across other fields.
    '''
