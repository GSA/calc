from django.core.management.base import BaseCommand

from contracts.models import Contract


class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        '''
        This normalizes Contract labor categories
        and then updates the full-text search indexes.
        '''

        print("Updating normalized labor categories...")
        Contract.objects.bulk_update_normalized_labor_categories()
