import urllib

from django.test import TestCase

from . import test_rates_api

RATES_CSV_PATH = '/api/rates/csv'


# TODO: These tests need to be more fully fleshed out
class GetRatesCSVTests(TestCase):
    def setUp(self):
        test_rates_api.GetRatesTests.make_test_set()
        self.path = RATES_CSV_PATH

    def test_prefixes_excel_formula_chars_in_query(self):
        excel_formula_prefixes = ['@', '+', '-', '=', '|', '%']
        for char in excel_formula_prefixes:
            encoded_query = urllib.parse.quote(f'{char}query')
            resp = self.client.get(f'{self.path}/?q={encoded_query}')
            self.assertContains(resp, f"'{char}query")

    def test_invalid_sort_field_raises_400(self):
        resp = self.client.get(f'{self.path}/?sort=sin')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), [
            'Unable to sort on the field "sin"'
        ])

    def test_unindexed_sort_field_raises_400(self):
        resp = self.client.get(f'{self.path}/?sort=blarg')
        self.assertEqual(resp.status_code, 400)
        self.assertEqual(resp.json(), [
            '"blarg" is not a valid field to sort on'
        ])
