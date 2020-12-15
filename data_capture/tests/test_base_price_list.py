from unittest.mock import patch
from unittest import TestCase

from ..schedules import base
from ..schedules.base import ConcreteBasePriceListMethods


class ConcreteBasePriceListMethodsTests(TestCase):
    def test_is_empty_returns_true_when_empty(self):
        pl = ConcreteBasePriceListMethods()
        self.assertTrue(pl.is_empty())

    def test_is_empty_returns_false_when_valid_rows_exist(self):
        pl = ConcreteBasePriceListMethods()
        pl.valid_rows = ['blah']
        self.assertFalse(pl.is_empty())

    def test_is_empty_returns_false_when_invalid_rows_exist(self):
        pl = ConcreteBasePriceListMethods()
        pl.invalid_rows = ['blah']
        self.assertFalse(pl.is_empty())

    def test_render_upload_example_returns_empty_string_by_default(self):
        self.assertEqual(ConcreteBasePriceListMethods.render_upload_example(),
                         '')

    def test_get_upload_example_context_returns_none_by_default(self):
        self.assertEqual(
            ConcreteBasePriceListMethods.get_upload_example_context(), None)

    @patch.object(base, 'render_to_string')
    def test_render_upload_example_calls_render_to_string(self, r):
        class FunkyPriceList(ConcreteBasePriceListMethods):
            upload_example_template = 'foo/bar.html'

        r.return_value = 'blah'

        self.assertEqual(FunkyPriceList.render_upload_example(), 'blah')

        r.assert_called_once_with('foo/bar.html', None, request=None)

    @patch.object(base, 'render_to_string')
    def test_render_upload_example_calls_get_upload_example_context(self, r):
        class FunkyPriceList(ConcreteBasePriceListMethods):
            upload_example_template = 'foo/bar.html'

            @classmethod
            def get_upload_example_context(cls):
                return {'foo': 'bar'}

        FunkyPriceList.render_upload_example('I am a fake request')
        r.assert_called_once_with('foo/bar.html', {'foo': 'bar'},
                                  request='I am a fake request')
