import json

from django.conf.urls import url
from django.http import HttpResponse
from django.test import TestCase, override_settings

from ..decorators import handle_cancel
from calc.urls import urlpatterns


@handle_cancel
def ok_view(request):
    return HttpResponse('ok')


@handle_cancel(redirect_name='another_view')
def redirect_name_view(request):
    return HttpResponse('ok no args')


@handle_cancel(key_prefix='another_prefix:')
def key_prefix_view(request):
    return HttpResponse('ok no args')


def index(request):
    return HttpResponse('index')


urlpatterns += [
    url(r'^test_view/$', ok_view),
    url(r'^another_view/$', index, name='another_view'),
    url(r'^redirect_name_view/$',
        redirect_name_view, name='redirect_name_view'),
    url(r'^key_prefix_view/$',
        key_prefix_view, name='key_prefix_view'),
    url(r'^$', index, name='index'),
    url(r'^login/$', ok_view, name='login')
]


@override_settings(ROOT_URLCONF=__name__)
class HandleCancelTests(TestCase):

    def setupSession(self, key_prefix='data_capture:'):
        session = self.client.session
        session['{}key_a'.format(key_prefix)] = 'value_a'
        session['{}key_b'.format(key_prefix)] = 'value_b'
        session['something_else'] = 'boop'
        session.save()

    def assertSessionOk(self, key_prefix='data_capture:'):
        session = self.client.session
        self.assertNotIn('{}key_a'.format(key_prefix), session)
        self.assertNotIn('{}key_b'.format(key_prefix), session)
        self.assertIn('something_else', session)

    def test_noop_when_not_post(self):
        res = self.client.get('/test_view/')
        self.assertEqual(200, res.status_code)
        self.assertEqual(b'ok', res.content)

    def test_noop_when_cancel_not_in_post(self):
        session = self.client.session
        session['data_capture:key_a'] = 'value_a'
        session.save()
        res = self.client.post('/test_view/')

        session = self.client.session
        self.assertEqual(200, res.status_code)
        self.assertEqual(b'ok', res.content)
        self.assertIn('data_capture:key_a', session)

    def test_removes_keys_from_session_on_post_cancel(self):
        self.setupSession()
        self.client.post('/test_view/', {'cancel': ''})
        self.assertSessionOk()

    def test_returns_redirect(self):
        res = self.client.post('/test_view/', {'cancel': ''})
        self.assertEqual(302, res.status_code)
        self.assertEqual(res['Location'], '/')

    def test_returns_json_redirect_when_ajax_post(self):
        res = self.client.post('/test_view/',
                               {'cancel': ''},
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(200, res.status_code)
        json_content = json.loads(res.content.decode('utf-8'))
        self.assertEqual(json_content, {
            'redirect_url': '/'
        })

    def test_works_with_key_prefix_specified(self):
        self.setupSession(key_prefix='another_prefix:')
        self.client.post('/key_prefix_view/', {'cancel': ''})
        self.assertSessionOk(key_prefix='another_prefix:')

    def test_works_with_redirect_name_specified(self):
        self.setupSession()
        res = self.client.post('/redirect_name_view/', {'cancel': ''})
        self.assertSessionOk()
        self.assertEqual(302, res.status_code)
        self.assertEqual(res['Location'], '/another_view/')
