from unittest import TestCase

from ..wsgi_middleware import static_url_rewriter


class StaticUrlRewriterTests(TestCase):
    def app(self, environ, start_response):
        start_response('200 OK', [])
        return ['hi from ' + environ['PATH_INFO']]

    def start_response(self, status, headers):
        self.status = status
        self.headers = headers

    def request(self, path_info):
        self.status = None
        self.headers = None
        self.environ = {'PATH_INFO': path_info}
        wrapper = static_url_rewriter(self.app, '/boop/', '/static/boop/')
        return wrapper(self.environ, self.start_response)

    def test_prefix_without_slash_redirects_to_prefix_with_slash(self):
        self.assertEqual(self.request('/boop'), [])
        self.assertEqual(self.status, '302 Found')
        self.assertEqual(self.headers, [('Location', '/boop/')])

    def test_paths_ending_in_slash_rewritten_to_end_with_index_html(self):
        self.assertEqual(self.request('/boop/'),
                         ['hi from /static/boop/index.html'])

    def test_paths_not_ending_in_slash_rewritten_to_dest_prefix(self):
        self.assertEqual(self.request('/boop/_meh/blarg.css'),
                         ['hi from /static/boop/_meh/blarg.css'])

    def test_paths_not_starting_with_prefix_are_not_rewritten(self):
        self.assertEqual(self.request('/zzzz/foo'),
                         ['hi from /zzzz/foo'])
