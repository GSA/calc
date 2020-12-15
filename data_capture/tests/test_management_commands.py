import io

from django.test import TestCase
from django.core.management import call_command
from django.contrib.auth.models import Group
from click.testing import CliRunner

from ..management.commands import initgroups, send_example_emails
from .common import R10_XLSX_PATH


class TestInitgroups(TestCase):
    def test_it_creates_group_iff_it_does_not_exist(self):
        output = io.StringIO()
        call_command('initgroups', stdout=output)
        self.assertRegex(output.getvalue(),
                         'Group does not exist, creating it.')

        output = io.StringIO()
        call_command('initgroups', stdout=output)
        self.assertNotRegex(output.getvalue(),
                            'Group does not exist, creating it.')

    def test_creates_expected_groups(self):
        output = io.StringIO()
        call_command('initgroups', stdout=output)
        for role in initgroups.ROLES:
            self.assertIsNotNone(Group.objects.get(name=role))


class TestSendexampleemails(TestCase):
    def test_it_does_not_explode(self):
        result = CliRunner().invoke(send_example_emails.command)
        self.assertEqual(result.exit_code, 0)


class TestSendtesthtmlemail(TestCase):
    def test_it_does_not_explode(self):
        call_command('send_test_html_email', 'foo@example.com')


class TestProcessBulkUpload(TestCase):
    def test_it_does_not_explode(self):
        call_command('process_bulk_upload', R10_XLSX_PATH)
