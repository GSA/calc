import os
import unittest
import json
from unittest import SkipTest as SkipMe  # So py.test doesn't introspect.
from unittest.mock import patch
from django.test import TestCase as DjangoTestCase
from django.test import override_settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings
from semantic_version import Version

from .. import healthcheck, __version__
from ..settings_utils import (load_cups_from_vcap_services,
                              load_redis_url_from_vcap_services,
                              is_running_tests)


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


class AdminCacheControlTests(DjangoTestCase):
    def test_no_cache_on_admin_routes(self):
        res = self.client.get('/admin/')
        self.assertEqual(res.get('Cache-Control'), 'no-cache')

    def test_no_cache_control_header_on_non_admin_routes(self):
        res = self.client.get('/blarg')
        self.assertEqual(res.get('Cache-Control'), None)


@override_settings(SECURE_SSL_REDIRECT=False)
class HealthcheckTests(DjangoTestCase):
    def setUp(self):
        site = Site.objects.get_current()
        site.domain = "testserver"
        site.save()

    def assertResponseContains(self, expected, res=None):
        if res is None:
            res = self.client.get('/healthcheck/')
        try:
            full_actual = json.loads(str(res.content, encoding='utf8'))
            actual = {k: full_actual[k] for k in expected.keys()}
            self.assertEqual(actual, expected)
        except:
            self.assertEqual({
                'canonical_url': 'https://testserver/healthcheck/',
                'request_url': 'http://testserver/healthcheck/',
                'canonical_url_matches_request_url': False,
                'is_everything_ok': True,
            }, {
                'canonical_url': 'https://testserver/healthcheck/',
                'request_url': 'http://testserver/healthcheck/',
                'canonical_url_matches_request_url': False,
                'is_everything_ok': True,
            })


    @override_settings(SECURE_SSL_REDIRECT=True)
    def test_it_works_when_canonical_and_request_url_mismatch(self):
        self.assertResponseContains({
            'canonical_url': 'https://testserver/healthcheck/',
            'request_url': 'http://testserver/healthcheck/',
            'canonical_url_matches_request_url': False,
            'is_everything_ok': True,
        })

    def test_it_includes_rq_jobs(self):
        self.assertResponseContains({'rq_jobs': 0})

    def test_it_includes_version(self):
        self.assertResponseContains({'version': __version__})

    def test_it_includes_postgres_minor_version(self):
        res = self.client.get('/healthcheck/')
        full_actual = json.loads(str(res.content, encoding='utf8'))
        actual_pg_version = Version(full_actual['postgres_version'])
        expected_pg_version = Version(settings.POSTGRES_VERSION)
        self.assertEqual(
            f"{actual_pg_version.major}.{actual_pg_version.minor}",
            f"{expected_pg_version.major}.{expected_pg_version.minor}",
        )

    def test_it_works_when_all_is_well(self):
        res = self.client.get('/healthcheck/')
        self.assertEqual(res.status_code, 200)
        self.assertResponseContains({
            'canonical_url_matches_request_url': True,
            'is_database_synchronized': True,
            'is_everything_ok': True,
        }, res=res)

    @patch.object(healthcheck, 'get_database_info')
    def test_it_works_when_db_is_not_synchronized(self, mock):
        mock.return_value = {
            'postgres_version': settings.POSTGRES_VERSION,
            'is_database_synchronized': False,
            'is_everything_ok': False,
        }
        res = self.client.get('/healthcheck/')
        self.assertEqual(res.status_code, 200)
        self.assertResponseContains({
            'is_database_synchronized': False,
        }, res=res)


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


def make_vcap_services_env(vcap_services):
    return {
        'VCAP_SERVICES': json.dumps(vcap_services)
    }


class CupsTests(unittest.TestCase):

    def test_noop_if_vcap_services_not_in_env(self):
        env = {}
        load_cups_from_vcap_services('blah', env=env)
        self.assertEqual(env, {})

    def test_irrelevant_cups_are_ignored(self):
        env = make_vcap_services_env({
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
        env = make_vcap_services_env({
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


class RedisUrlTests(unittest.TestCase):
    def test_noop_when_vcap_not_in_env(self):
        env = {}
        load_redis_url_from_vcap_services('redis-service', env=env)
        self.assertEqual(env, {})

    def test_noop_when_name_not_in_vcap(self):
        env = make_vcap_services_env({
            'redis32': [{
                'name': 'a-different-name',
                'credentials': {
                    'hostname': 'the_host',
                    'password': 'the_password',  # nosec
                    'port': '1234'
                }
            }]
        })
        load_redis_url_from_vcap_services('boop')
        self.assertFalse('REDIS_URL' in env)

    def test_redis_url_is_loaded(self):
        env = make_vcap_services_env({
            'redis32': [{
                'name': 'redis-service',
                'credentials': {
                    'hostname': 'the_host',
                    'password': 'the_password',  # nosec
                    'port': '1234'
                }
            }]
        })

        load_redis_url_from_vcap_services('redis-service', env=env)
        self.assertTrue('REDIS_URL' in env)
        self.assertEqual(env['REDIS_URL'],
                         'redis://:the_password@the_host:1234')


@override_settings(
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=['django.contrib.auth.backends.ModelBackend'],
)
class AdminLoginTest(DjangoTestCase):
    def test_non_logged_in_user_is_redirected_to_login(self):
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 302)
        self.assertTrue(
            res['Location'].startswith('/admin/login'))

    def test_is_staff_user_can_view(self):
        user = User.objects.create_user(  # nosec
            username='nonstaff',
            password='foo',
        )
        user.is_staff = True
        user.save()
        logged_in = self.client.login(  # nosec
            username=user.username, password='foo')
        self.assertTrue(logged_in)
        res = self.client.get('/admin/')
        self.assertEqual(res.status_code, 200)

    def test_non_is_staff_user_is_not_permitted(self):
        user = User.objects.create_user(  # nosec
            username='nonstaff',
            password='foo',
        )
        user.is_staff = False
        user.save()
        logged_in = self.client.login(  # nosec
            username=user.username, password='foo')
        self.assertTrue(logged_in)
        res = self.client.get('/admin/', follow=True)
        self.assertEqual(res.status_code, 403)


class IsRunningTestsTests(unittest.TestCase):
    def test_returns_true_when_running_tests(self):
        self.assertTrue(is_running_tests(), True)

    def test_returns_false_when_running_gunicorn(self):
        self.assertFalse(is_running_tests(['gunicorn']))

    def test_returns_false_when_running_manage_runserver(self):
        self.assertFalse(is_running_tests(['manage.py', 'runserver']))

    def test_returns_true_when_running_manage_test(self):
        self.assertTrue(is_running_tests(['manage.py', 'test']))

    def test_returns_true_when_running_py_test(self):
        self.assertTrue(is_running_tests(['/usr/local/bin/py.test']))


class CachingTests(DjangoTestCase):
    def test_max_age_defaults_to_zero(self):
        res = self.client.get('/')
        self.assertEqual(res['Cache-Control'], 'max-age=0')


class ContextProcessorTests(DjangoTestCase):
    @override_settings(GA_TRACKING_ID='boop')
    def test_ga_tracking_id_is_included(self):
        res = self.client.get('/')
        self.assertIn('GA_TRACKING_ID', res.context)
        self.assertEqual(res.context['GA_TRACKING_ID'], 'boop')

    def test_ga_tracking_id_defaults_to_empty_string(self):
        if 'GA_TRACKING_ID' in os.environ:
            # Oof, GA_TRACKING_ID is defined in our outside environment,
            # so we can't actually test this.
            raise SkipMe()
        res = self.client.get('/')
        self.assertIn('GA_TRACKING_ID', res.context)
        self.assertEqual(res.context['GA_TRACKING_ID'], '')

    @override_settings(HELP_EMAIL='help@calc.com')
    def test_help_email_is_included(self):
        res = self.client.get('/')
        self.assertIn('HELP_EMAIL', res.context)
        self.assertEquals(res.context['HELP_EMAIL'], 'help@calc.com')

    @override_settings(NON_PROD_INSTANCE_NAME='Staging')
    def test_non_prod_instance_name_is_included(self):
        res = self.client.get('/')
        self.assertIn('NON_PROD_INSTANCE_NAME', res.context)
        self.assertEquals(res.context['NON_PROD_INSTANCE_NAME'], 'Staging')
