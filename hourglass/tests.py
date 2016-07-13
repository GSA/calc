import unittest
import json
from django.test import TestCase as DjangoTestCase
from django.test import override_settings

from .settings_utils import load_cups_from_vcap_services, get_whitelisted_ips


class ComplianceTests(DjangoTestCase):
    '''
    These tests ensure our site is configured with proper regulatory
    compliance and security best practices.  For more information, see:

    https://compliance-viewer.18f.gov/

    Cloud.gov's nginx proxy adds the required headers to 200 responses, but
    not to responses with error codes, so we need to add them at the app-level.
    '''

    headers = {
        'X-Content-Type-Options': 'nosniff',
        'X-XSS-Protection': '1; mode=block',
    }

    def assertHasHeaders(self, res):
        for header, val in self.headers.items():
            self.assertEqual(res[header], val)

    @override_settings(SECURITY_HEADERS_ON_ERROR_ONLY=False)
    def test_has_security_headers(self):
        res = self.client.get('/')
        self.assertHasHeaders(res)

    @override_settings(SECURITY_HEADERS_ON_ERROR_ONLY=False)
    def test_has_security_headers_on_404(self):
        res = self.client.get('/i-am-a-nonexistent-page')
        self.assertHasHeaders(res)

    @override_settings(SECURITY_HEADERS_ON_ERROR_ONLY=True)
    def test_no_security_headers_when_setting_enabled(self):
        res = self.client.get('/')
        for header, val in self.headers.items():
            self.assertNotIn(header, res)

    @override_settings(SECURITY_HEADERS_ON_ERROR_ONLY=True)
    def test_has_security_headers_on_404_when_setting_enabled(self):
        res = self.client.get('/i-am-a-nonexistent-page')
        self.assertHasHeaders(res)


class RobotsTests(DjangoTestCase):
    @override_settings(ENABLE_SEO_INDEXING=False)
    def test_disable_seo_indexing_works(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b"User-agent: *\nDisallow: /")

    @override_settings(ENABLE_SEO_INDEXING=True)
    def test_enable_seo_indexing_works(self):
        res = self.client.get('/robots.txt')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.content, b"User-agent: *\nDisallow:")


class CupsTests(unittest.TestCase):
    @staticmethod
    def make_vcap_services_env(vcap_services):
        return {
            'VCAP_SERVICES': json.dumps(vcap_services)
        }

    def test_noop_if_vcap_services_not_in_env(self):
        env = {}
        load_cups_from_vcap_services('blah', env=env)
        self.assertEqual(env, {})

    def test_irrelevant_cups_are_ignored(self):
        env = self.make_vcap_services_env({
          "user-provided": [
            {
              "label": "user-provided",
              "name": "NOT-boop-env",
              "syslog_drain_url": "",
              "credentials": {
                "boop": "jones"
              },
              "tags": []
            }
          ]
        })

        load_cups_from_vcap_services('boop-env', env=env)

        self.assertFalse('boop' in env)

    def test_credentials_are_loaded(self):
        env = self.make_vcap_services_env({
          "user-provided": [
            {
              "label": "user-provided",
              "name": "boop-env",
              "syslog_drain_url": "",
              "credentials": {
                "boop": "jones"
              },
              "tags": []
            }
          ]
        })

        load_cups_from_vcap_services('boop-env', env=env)

        self.assertEqual(env['boop'], 'jones')


class GetWhitelistedIPsTest(unittest.TestCase):
    def test_returns_none_when_not_in_env(self):
        env = {}
        self.assertIsNone(get_whitelisted_ips(env))

    def test_returns_whitelisted_ips_list(self):
        env = {
            'WHITELISTED_IPS': '1.2.3.4,1.2.3.8, 1.2.3.16'
        }
        ips = get_whitelisted_ips(env)
        self.assertListEqual(ips, ['1.2.3.4', '1.2.3.8', '1.2.3.16'])
