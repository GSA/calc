from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from django.utils.safestring import SafeText

from contracts.models import ScheduleMetadata


def populate_schedule_metadata():
    # This is SUPER weird. Previous TransactionTestCase runs (usually
    # the result of a LiveServerTestCase) could have removed the
    # schedule metadata populated by our migration, so we'll forcibly
    # wipe our schedule metadata and re-run the migration just in case.

    ScheduleMetadata.objects.all().delete()
    call_command('migrate', 'contracts', '0023_schedulemetadata', '--fake')
    call_command('migrate', 'contracts', '0024_populate_schedulemetadata')
    call_command('migrate', '--fake')


class InitialScheduleMetadataTests(TestCase):
    def test_populate_data_migration_works(self):
        populate_schedule_metadata()
        env = ScheduleMetadata.objects.get(sin='899')
        self.assertEqual(env.schedule, 'Environmental')
        self.assertEqual(env.name, 'Legacy Environmental')
        self.assertIn('pollution', env.description)
        self.assertEqual(list(
            sm.schedule
            for sm in ScheduleMetadata.objects.all().order_by('schedule')
        ), [
            'AIMS',
            'Consolidated',
            'Environmental',
            'FABS',
            'IT Schedule 70',
            'Language Services',
            'Logistics',
            'MOBIS',
            'PES',
        ])


class SimpleTests(SimpleTestCase):
    def test_description_html_works(self):
        sm = ScheduleMetadata(description='hello *there*')
        self.assertEqual(
            sm.description_html,
            '<p>hello <em>there</em></p>'
        )
        self.assertIsInstance(sm.description_html, SafeText)
