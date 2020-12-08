import io
from django.core.management import call_command, CommandError
from django.test import LiveServerTestCase, SimpleTestCase, override_settings
from httmock import all_requests, response, HTTMock

from contracts.mommy_recipes import get_contract_recipe
from contracts.models import Contract
from api.management.commands.load_api_data import (
    iter_api_pages,
    Command,
)


# These tests are a bit funky because we run the command against its
# own API, which means that we can run into weird situations like
# infinite loops if we're not careful.
#
# Ideally we'd be able to set up *two* databases, one which the
# command runs against and another which the live server runs
# against. But since that's not possible, we'll just do this.
class LiveServerTests(LiveServerTestCase):
    def test_loading_from_empty_db_works(self):
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            append=True,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            f'No rates were written to the database'
        )

    @override_settings(PAGINATION=2)
    def test_retrieving_multiple_pages_works(self):
        get_contract_recipe().make(_quantity=5)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            dry_run=True,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            'Processed 5 rates in dry run mode over 3 pages'
        )

    @override_settings(PAGINATION=2)
    def test_stops_retrieving_at_end_page(self):
        get_contract_recipe().make(_quantity=5)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            dry_run=True,
            end_page=1,
            stdout=stdout
        )
        self.assertRegex(
            stdout.getvalue(),
            'Processed 2 rates in dry run mode over 1 pages'
        )

    def test_rewriting_from_self_is_empty_db(self):
        get_contract_recipe().make()
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            stdout=stdout
        )
        self.assertEquals(Contract.objects.count(), 0)
        self.assertRegex(
            stdout.getvalue(),
            f'Deleting all existing rate information'
        )
        self.assertRegex(
            stdout.getvalue(),
            f'No rates were written to the database'
        )

    def test_appending_from_self_doubles_contract_count(self):
        count = 5
        get_contract_recipe().make(_quantity=count)
        stdout = io.StringIO()
        call_command(
            'load_api_data',
            url=f"{self.live_server_url}/api/rates/",
            append=True,
            stdout=stdout
        )
        self.assertEquals(Contract.objects.count(), count * 2)
        self.assertRegex(
            stdout.getvalue(),
            f'Done writing {count} rates to the database'
        )


def json_200(content):
    @all_requests
    def response_content(url, request):
        headers = {'content-type': 'application/json'}
        return response(200, content, headers)

    return response_content


EMPTY_RESPONSE = {
    'count': 0,
    'results': [],
    'next': None,
}


ONE_BAD_RESPONSE = {
    'count': 1,
    'results': [{
        'id': 123,
        'foo': 'blah',
    }],
    'next': None,
}


class SimpleTests(SimpleTestCase):
    def test_start_page_must_be_leq_end_page(self):
        msg = 'Start page cannot be greater than end page'
        with self.assertRaisesRegex(CommandError, msg):
            call_command('load_api_data', start_page=5, end_page=1)

    def test_iter_api_pages_results_are_ok(self):
        with HTTMock(json_200(ONE_BAD_RESPONSE)):
            results, total = next(iter_api_pages('http://blah'))
            self.assertEqual(results, [{'foo': 'blah'}])

    def test_total_pages_is_correct_when_end_page_is_too_high(self):
        with HTTMock(json_200(EMPTY_RESPONSE)):
            results, total = next(iter_api_pages('http://blah', end_page=99))
            self.assertEqual(total, 1)

    def test_process_pages_works_if_pages_is_empty(self):
        cmd = Command()
        self.assertEqual(cmd.process_pages([], False), (0, 0))

    def test_process_pages_logs_errors(self):
        stderr = io.StringIO()
        cmd = Command(stderr=stderr)
        num_rates, num_pages = cmd.process_pages([
            ([ONE_BAD_RESPONSE], 1)
        ], False)
        self.assertEqual(num_rates, 0)
        self.assertEqual(num_pages, 1)
        self.assertRegex(
            stderr.getvalue(),
            r'Rate .*blah.* has error .*This field is required.*'
        )
