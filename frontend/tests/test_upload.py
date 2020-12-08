from django.test import SimpleTestCase

from ..upload import UploadWidget


class UploadWidgetTests(SimpleTestCase):
    def test_error_raised_if_required_and_existing_filename(self):
        uw = UploadWidget(existing_filename='boop.csv')
        with self.assertRaises(AssertionError):
            uw.render('a', 'b')

    def test_existing_filename_works(self):
        uw = UploadWidget(existing_filename='boop.csv', required=False)
        html = uw.render('a', 'b')
        assert "You've already uploaded" in html
        assert 'data-fake-initial-filename="boop.csv"' in html
