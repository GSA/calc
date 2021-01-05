from django.test import override_settings

from calc.urls import urlpatterns, tests_url
from .test_selenium import SeleniumTestCase


urlpatterns += [tests_url]

TESTS_URL = '/tests/?hidepassed'


@override_settings(ROOT_URLCONF=__name__)
class QunitTests(SeleniumTestCase):
    '''
    Run QUnit tests in a real-world browser via Selenium.
    '''

    def test_qunit(self):
        self.load(TESTS_URL)

        FAILED = '#qunit-testresult .failed'

        def are_results_loaded():
            els = self.driver.find_elements_by_css_selector(FAILED)

            return len(els) > 0

        self.wait_for(are_results_loaded)

        failed = self.driver.find_element_by_css_selector(FAILED).text

        if failed != '0':
            raise Exception("{} qunit test(s) failed".format(failed))
