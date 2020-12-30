from django.test import TestCase

from ..loaders.region_10 import Region10Loader


class Region10LoaderTests(TestCase):
    def test_error_raised_if_labor_category_is_missing(self):
        with self.assertRaisesRegexp(ValueError, 'missing labor category'):
            Region10Loader.make_contract([''])
