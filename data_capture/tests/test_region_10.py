import json

from decimal import Decimal

from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from .common import path, uploaded_xlsx_file, FakeWorkbook, FakeSheet
from .test_models import ModelTestCase
from ..schedules import region_10 as r10, registry

R10 = '{}.Region10PriceList'.format(r10.__name__)

R10_XLSX_PATH = path('static', 'data_capture', 'r10_example.xlsx')

# TODO: These tests should be DRY'd out since they nearly identical to test_s70
# Or really the shared methods should be generalized and those should be
# tested.


class GleaningTests(TestCase):
    def create_fake_book(self):
        return FakeWorkbook(sheets=[
            FakeSheet(r10.DEFAULT_SHEET_NAME, r10.EXAMPLE_SHEET_ROWS)])

    def test_rows_are_returned(self):
        rows = r10.glean_labor_categories_from_file(
            uploaded_xlsx_file(R10_XLSX_PATH))

        self.assertEqual(rows, [{
            'education_level': 'Bachelors',
            'sin': '123-1',
            'min_years_experience': '2',
            'labor_category': 'Consultant II',
            'unit_of_issue': 'Hour',
            'price_including_iff': '90.68'
        }, {
            'education_level': '',
            'sin': '123-2',
            'min_years_experience': '0',
            'labor_category': 'Disposal Services',
            'unit_of_issue': 'Task',
            'price_including_iff': '0.0'
        }])

    def test_text_formatted_prices_are_gleaned(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][13] = '$  37.50 '
        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['price_including_iff'], '37.50')

    def test_min_education_is_gleaned_from_text(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][2] = 'GED or high school or whatever'
        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['education_level'], 'High School')

    def test_unit_of_issue_is_gleaned_to_hour(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][7] = 'Hourly'

        rows = r10.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['unit_of_issue'], 'Hour')

    def test_validation_error_raised_when_sheet_not_present(self):
        with self.assertRaisesRegexp(
            ValidationError,
            r'There is no sheet in the workbook called "foo"'
        ):
            r10.glean_labor_categories_from_file(
                uploaded_xlsx_file(R10_XLSX_PATH),
                sheet_name='foo'
            )


@override_settings(DATA_CAPTURE_SCHEDULES=[R10])
class Region10PriceListTests(ModelTestCase):
    DEFAULT_SCHEDULE = R10

    def test_valid_rows_are_populated(self):
        p = r10.Region10PriceList.load_from_upload(
            uploaded_xlsx_file(R10_XLSX_PATH))

        self.assertEqual(len(p.valid_rows), 1)
        self.assertEqual(len(p.invalid_rows), 1)

        self.assertEqual(p.valid_rows[0].cleaned_data, {
            'education_level': 'Bachelors',
            'labor_category': 'Consultant II',
            'min_years_experience': 2,
            'price_including_iff': Decimal('90.68'),
            'sin': '123-1',
            'unit_of_issue': 'Hour'
        })

    def test_education_level_is_validated(self):
        p = r10.Region10PriceList(rows=[{'education_level': 'Batchelorz'}])

        self.assertRegexpMatches(
            p.invalid_rows[0].errors['education_level'][0],
            r'This field must contain one of the following values'
        )

    def test_price_including_iff_is_validated(self):
        p = r10.Region10PriceList(rows=[{'price_including_iff': '1.10'}])
        self.assertRegexpMatches(
            p.invalid_rows[0].errors['price_including_iff'][0],
            r'Price must be at least'
        )

    def test_min_years_experience_is_validated(self):
        p = r10.Region10PriceList(rows=[{'min_years_experience': ''}])

        self.assertEqual(p.invalid_rows[0].errors['min_years_experience'],
                         ['This field is required.'])

    def test_unit_of_issue_is_validated(self):
        p = r10.Region10PriceList(rows=[{'unit_of_issue': ''}])
        self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                         ['This field is required.'])

        p = r10.Region10PriceList(rows=[{'unit_of_issue': 'Day'}])
        self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                         ['Value must be "Hour" or "Hourly"'])

    def test_unit_of_issue_can_be_hour_or_hourly(self):
        p = r10.Region10PriceList(rows=[{'unit_of_issue': 'Hour'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

        p = r10.Region10PriceList(rows=[{'unit_of_issue': 'hourly'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

    def test_add_to_price_list_works(self):
        s = r10.Region10PriceList.load_from_upload(
            uploaded_xlsx_file(R10_XLSX_PATH))

        p = self.create_price_list()
        p.save()

        s.add_to_price_list(p)

        row = p.rows.all()[0]

        self.assertEqual(row.labor_category, 'Consultant II')
        self.assertEqual(row.education_level, 'BA')
        self.assertEqual(row.min_years_experience, 2)
        self.assertEqual(row.base_year_rate, Decimal('90.68'))
        self.assertEqual(row.sin, '123-1')

        row.full_clean()

    def test_serialize_and_deserialize_work(self):
        s = r10.Region10PriceList.load_from_upload(
            uploaded_xlsx_file(R10_XLSX_PATH))

        saved = json.dumps(registry.serialize(s))
        restored = registry.deserialize(json.loads(saved))

        self.assertTrue(isinstance(restored, r10.Region10PriceList))
        self.assertEqual(s.rows, restored.rows)

    def test_to_table_works(self):
        s = r10.Region10PriceList.load_from_upload(
            uploaded_xlsx_file(R10_XLSX_PATH))
        table_html = s.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_to_error_table_works(self):
        s = r10.Region10PriceList.load_from_upload(
            uploaded_xlsx_file(R10_XLSX_PATH))
        table_html = s.to_error_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_render_upload_example_works(self):
        html = r10.Region10PriceList.render_upload_example()
        for row in r10.EXAMPLE_SHEET_ROWS:
            for col in row:
                self.assertIn(col, html)
