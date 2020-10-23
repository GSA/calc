from django.test import override_settings, TestCase

from ..site_utils import absolute_reverse, absolutify_url


class SiteUtilsTests(TestCase):
    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=True)
    def test_absolute_reverse_works(self):
        self.assertEqual(
            absolute_reverse('data_capture:step_1'),
            'https://example.com/data-capture/step/1'
        )

    def test_absolutify_url_raises_error_on_non_absolute_paths(self):
        with self.assertRaises(ValueError):
            absolutify_url('meh')

    def test_absolutify_url_passes_through_http_urls(self):
        self.assertEqual(absolutify_url('http://foo'), 'http://foo')

    def test_absolutify_url_passes_through_https_urls(self):
        self.assertEqual(absolutify_url('https://foo'), 'https://foo')

    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=True)
    def test_absolutify_url_works_in_production(self):
        self.assertEqual(
            absolutify_url('/boop'),
            'https://example.com/boop'
        )

    @override_settings(DEBUG=False, SECURE_SSL_REDIRECT=False)
    def test_absolutify_url_works_in_unencrypted_production(self):
        self.assertEqual(
            absolutify_url('/boop'),
            'http://example.com/boop'
        )

    @override_settings(DEBUG=True, SECURE_SSL_REDIRECT=False)
    def test_absolutify_url_works_in_development(self):
        self.assertEqual(
            absolutify_url('/blap'),
            'http://example.com/blap'
        )

    @override_settings(DEBUG=True, DEBUG_HTTPS=True,
                       SECURE_SSL_REDIRECT=True)
    def test_absolutify_url_works_when_debug_https_is_true(self):
        self.assertEqual(
            absolutify_url('/blap'),
            'https://example.com/blap'
        )
