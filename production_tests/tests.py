from urllib.parse import urlparse, parse_qs

from .util import ProductionTestCase


class ProductionTests(ProductionTestCase):
    def test_oauth2_redirect_uri_has_correct_domain(self):
        '''
        Mitigation against https://github.com/18F/calc/pull/1187.
        '''

        res = self.client.get('/auth/login')
        self.assertEqual(res.status_code, 302)
        qs = parse_qs(urlparse(res.headers['Location']).query)
        o = urlparse(qs['redirect_uri'][0])
        origin = o.scheme + '://' + o.netloc
        self.assertEqual(origin, self.ORIGIN)

    def test_index_has_short_expiry(self):
        '''
        Mitigation against https://github.com/18F/calc/issues/1257.
        '''

        res = self.client.get('/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.headers['Cache-Control'],
                         'max-age=0')

    def test_static_files_have_long_expiry(self):
        '''
        This ensures that our static files have a very long expiry,
        which should be the case since the hash of their contents is
        part of their URL.
        '''

        res = self.client.get(
            # This particular file will rarely, if ever, change, so
            # we'll just hardcode its hash here.
            '/static/frontend/images/flag-usa.9db9ec00aaa0.png'
        )
        self.assertEqual(res.status_code, 200)

        cc = [s.strip() for s in res.headers['Cache-Control'].split(',')]

        self.assertIn('max-age=315360000', cc)
        self.assertIn('public', cc)

    def test_ajaxform_submission_works(self):
        '''
        This basically ensures that the 'X-Requested-With' header is
        being passed through any reverse proxies, so that our
        progressively-enhanced Ajax forms can detect whether they're
        being accessed via Ajax or not.
        '''

        self.browser.open('/styleguide/ajaxform')
        self.browser.session.headers['Referer'] = self.ORIGIN
        self.browser.session.headers['X-Requested-With'] = 'XMLHttpRequest'
        form = self.browser.get_form()
        self.browser.submit_form(form)
        self.assertEqual(self.browser.response.status_code, 200)
        self.assertIn('form_html', self.browser.response.json())

    def test_form_submission_works(self):
        '''
        Mitigation against https://github.com/18F/calc/issues/1198.
        '''

        self.browser.open('/styleguide/radio-checkbox')
        self.browser.session.headers['Referer'] = self.ORIGIN
        form = self.browser.get_form()
        form['radios'].value = '2'
        form['checkboxes'].value = 'a'
        self.browser.submit_form(form)
        self.assertEqual(self.browser.response.status_code, 200)
        self.assertIn('You chose radio option #2!',
                      self.browser.response.content.decode('utf-8'))

    def test_api_supports_cors(self):
        '''
        Mitigation against https://github.com/18F/calc/issues/1307.
        '''
        res = self.client.get(
            '/api/search/?format=json&q=zzzzzzzz&query_type=match_all',
            headers={'Origin': self.ORIGIN}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])
        self.assertEqual(res.headers['Access-Control-Allow-Origin'], '*')

    def test_api_passes_json_accept_header(self):
        res = self.client.get(
            '/api/search/?q=zzzzzzzz&query_type=match_all',
            headers={'Accept': 'application/json'}
        )
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])
        self.assertEqual(res.headers['Content-Type'], 'application/json')
