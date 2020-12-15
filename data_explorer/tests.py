from unittest import mock
from django.test import TestCase
from django.contrib.auth.models import User


class DataExplorerTests(TestCase):
    def test_logout_works(self):
        with mock.patch('django.contrib.auth.logout') as logout_mock:
            response = self.client.get('/logout/')
            self.assertEqual(response.status_code, 200)
            self.assertEqual(logout_mock.call_count, 1)

    def test_dap_is_part_of_unauthenticated_requests(self):
        response = self.client.get('/')
        self.assertContains(response, 'dap.digitalgov.gov')

    def test_dap_is_not_part_of_authenticated_requests(self):
        user = User.objects.create_user('blarg')
        self.client.force_login(user)
        response = self.client.get('/')
        self.assertNotContains(response, 'dap.digitalgov.gov')

    def test_og_status(self):
        """
        Ensure `head_meta` tag is writing to response as expected.

        We're logging in so there's no weirdness caused by a redirect to a
        login page or similar shenanigans.

        We're checking og:site_name string because (a) it should
        only be present if the tag worked and (b) it should be stable and
        relatively unchanging over time.
        """
        user = User.objects.create_user('blarg')
        self.client.force_login(user)
        # Now test index. We test this last because Selenium expects
        # tests to end at the index for reasons.
        response = self.client.get('/')
        self.assertContains(
            response,
            '<meta property="og:site_name" content="Contract-Awarded Labor Category (CALC)">'
        )
        # Check /about, too. We should consider reversing the url name.
        response = self.client.get('/about/')
        self.assertContains(response, '<title>CALC / About CALC</title>')
