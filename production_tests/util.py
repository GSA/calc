from unittest import TestCase
import requests
from robobrowser import RoboBrowser


class ProductionHttpClient:
    '''
    A basic HTTP client that defaults to the given origin.
    '''

    def __init__(self, origin):
        self.origin = origin

    def get(self, url, *args, **kwargs):
        if url.startswith('/'):
            url = self.origin + url
        if 'allow_redirects' not in kwargs:
            kwargs['allow_redirects'] = False
        return requests.get(url, *args, **kwargs)


class ProductionBrowser(RoboBrowser):
    '''
    A RoboBrowser subclass that defaults to the given origin.
    '''

    def __init__(self, origin, *args, **kwargs):
        self.origin = origin
        super().__init__(*args, **kwargs)

    def open(self, url):
        if url.startswith('/'):
            url = self.origin + url
        return super().open(url)


class ProductionTestCase(TestCase):
    '''
    A base test case whose utilities default to a production deployment
    of CALC.
    '''

    # This will be set by test runner code.
    ORIGIN = None

    def setUp(self):
        self.client = ProductionHttpClient(self.ORIGIN)
        self.browser = ProductionBrowser(self.ORIGIN, history=True,
                                         parser='html.parser')
