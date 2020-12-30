from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from robobrowser import RoboBrowser
from robobrowser.forms.form import Form

from . import base


class RoboBrowserForm(base.AbstractBrowserForm):
    def __init__(self, browser, selector):
        self.browser = browser
        self.form_el = self.browser.select(selector)[0]
        self.form = Form(self.form_el)

    def set_text(self, name, value):
        self.form[name] = value

    def set_radio(self, name, number):
        radio = self.form_el.find(id=self.get_id_for_radio(
            name,
            number
        ))
        self.form[name] = radio['value']

    def set_file(self, name, path):
        self.form[name] = open(path, 'r')

    def submit(self):
        self.browser.submit_form(self.form)


class RoboBrowserTestCase(StaticLiveServerTestCase, base.AbstractBrowser):
    def setUp(self):
        super().setUp()
        self.browser = RoboBrowser(history=True, parser='html.parser')

    def load(self, url):
        self.browser.open(self.live_server_url + url)

    def get_title(self):
        return self.browser.find('title').text

    def get_form(self, selector):
        return RoboBrowserForm(self.browser, selector)
