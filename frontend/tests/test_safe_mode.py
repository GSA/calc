import unittest
from unittest.mock import patch
import django.test

from .. import safe_mode
from ..context_processors import is_safe_mode_enabled


class FakeRequest:
    def __init__(self, **kwargs):
        self.session = kwargs


class UrlTests(django.test.TestCase):
    def test_enable_works(self):
        res = self.client.post('/safe-mode/enable')
        self.assertTrue(self.client.session['enable_safe_mode'])
        self.assertRedirects(res, '/')

    def test_disable_works(self):
        res = self.client.post('/safe-mode/disable')
        self.assertFalse(self.client.session['enable_safe_mode'])
        self.assertRedirects(res, '/')

    def test_endpoints_redirect_to_referrer_if_present(self):
        for path in ['/safe-mode/enable', '/safe-mode/disable']:
            res = self.client.post(path, HTTP_REFERER='/foo')
            self.assertRedirects(res, '/foo', fetch_redirect_response=False)


class SimpleTests(unittest.TestCase):
    def test_is_enabled_returns_false_by_default(self):
        self.assertFalse(safe_mode.is_enabled(FakeRequest()))

    def test_is_enabled_returns_session_key_value(self):
        self.assertTrue(
            safe_mode.is_enabled(FakeRequest(enable_safe_mode=True))
        )
        self.assertFalse(
            safe_mode.is_enabled(FakeRequest(enable_safe_mode=False))
        )

    @patch.object(safe_mode, 'is_enabled')
    def test_context_processor_delegates_to_is_enabled(self, is_enabled):
        is_enabled.return_value = 'sure buddy'

        req = FakeRequest()
        ctx = is_safe_mode_enabled(req)
        self.assertEqual(ctx, {
            'is_safe_mode_enabled': 'sure buddy'
        })
        is_enabled.assert_called_once_with(req)
