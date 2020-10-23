from itertools import cycle
from django.test import TestCase

from ..views import GetAutocomplete
from contracts.mommy_recipes import get_contract_recipe


class GetAutocompleteTests(TestCase):
    '''
    Tests for the autocomplete endpoint
    TODO: More tests are needed:
        - different query_type params
        - 'count' property of returned results
        - ordering of results
    '''

    path = '/api/search/'

    def make_test_contracts(self, quantity=1):
        labor_cat_names = [f"test_{i}" for i in range(0, quantity)]
        get_contract_recipe().make(
            _quantity=quantity,
            labor_category=cycle(labor_cat_names)
        )

    def test_path_works(self):
        res = self.client.get(self.path)
        self.assertEqual(res.status_code, 200)

    def test_returns_empty_if_no_query(self):
        get_contract_recipe().make(
            labor_category='test'
        )
        res = self.client.get(self.path)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(res.json(), [])

    def test_returns_json_results(self):
        self.make_test_contracts()
        res = self.client.get(self.path + '?q=te')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), 1)
        self.assertEqual(data[0], {
            'labor_category': 'test_0',
            'count': 1,
        })

    def test_limits_results_length_to_MAX_RESULTS(self):
        quantity = GetAutocomplete.MAX_RESULTS * 2
        self.make_test_contracts(quantity)
        res = self.client.get(self.path + '?q=test')
        self.assertEqual(res.status_code, 200)
        data = res.json()
        self.assertEqual(len(data), GetAutocomplete.MAX_RESULTS)
