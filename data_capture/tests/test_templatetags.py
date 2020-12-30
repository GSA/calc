from datetime import datetime

from django.test import TestCase, override_settings

from ..templatetags.data_capture import tz_timestamp
from ..templatetags.email_utils import absolute_static


class ReadableTimestampTests(TestCase):
    def test_it_works(self):
        utc_datetime = datetime(2016, 2, 3, 14, 30, 5)
        val = tz_timestamp(utc_datetime)
        self.assertEqual(val, 'Feb. 3, 2016 at 9:30 a.m. (EST)')

    def test_it_returns_orig_value_when_not_datetime(self):
        val = tz_timestamp('abc')
        self.assertEqual(val, 'abc')

    def test_timezone_name_can_be_specified(self):
        utc_datetime = datetime(2016, 2, 11, 14, 30, 5)
        val = tz_timestamp(utc_datetime, "US/Central")
        self.assertEqual(val, 'Feb. 11, 2016 at 8:30 a.m. (CST)')


@override_settings(SECURE_SSL_REDIRECT=False)
class EmailUtilsTests(TestCase):
    def test_absolute_static_works(self):
        self.assertEqual(
            absolute_static('frontend/images/flag-usa.png'),
            'http://example.com/static/frontend/images/flag-usa.png'
        )
