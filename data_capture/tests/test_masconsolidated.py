import json
import html as html_module
from decimal import Decimal

from .common import path, uploaded_xlsx_file, FakeWorkbook, FakeSheet
from .test_models import ModelTestCase
from ..schedules import mas_consolidated as mas, registry
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError
MAS = '{}.MASConsolidatedPriceList'.format(mas.__name__)
file_name = 'Price_Proposal_Template_SERVICES_AND_TRAINING_102919.xlsx'
MAS_XLSX_PATH = path('static', 'data_capture', file_name)

# TODO: These tests should be DRY'd out since they nearly identical to test_s70
# Or really the shared methods should be generalized and those should be
# tested.


class GleaningTests(TestCase):
    def create_fake_book(self):
        return FakeWorkbook(sheets=[
            FakeSheet(mas.DEFAULT_SHEET_NAME, mas.EXAMPLE_SHEET_ROWS)])

    def test_rows_are_returned(self):
        rows = mas.glean_labor_categories_from_file(
            uploaded_xlsx_file(MAS_XLSX_PATH))
        self.assertEqual(rows, [{
            'sin': '874-1',
            'labor_category': 'Principal Consultant',
            'education_level': 'Bachelors',
            'min_years_experience': '10',
            'unit_of_issue': 'Hour',
            'price_including_iff': '200.0',
            'keywords': 'Process improvement, finance, senior project manager',
            'certifications': 'PMP',
            'security_clearance': 'No'
        }])

    def test_text_formatted_prices_are_gleaned(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][13] = '$  200.00 '
        rows = mas.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['price_including_iff'], '200.00')

    def test_min_education_is_gleaned_from_text(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][2] = 'GED or high school'
        rows = mas.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['education_level'], 'Bachelors')

    def test_unit_of_issue_is_gleaned_to_hour(self):
        book = self.create_fake_book()
        book._sheets[0]._cells[1][7] = 'Hourly'

        rows = mas.glean_labor_categories_from_book(book)
        self.assertEqual(rows[0]['unit_of_issue'], 'Hour')

    def test_validation_error_raised_when_sheet_not_present(self):
        with self.assertRaisesRegexp(
            ValidationError,
            r'There is no sheet in the workbook called "foo"'
        ):
            mas.glean_labor_categories_from_file(
                uploaded_xlsx_file(MAS_XLSX_PATH),
                sheet_name='foo'
            )


@override_settings(DATA_CAPTURE_SCHEDULES=[MAS])
class MASConsolidatedPriceListTests(ModelTestCase):
    DEFAULT_SCHEDULE = MAS

    def test_valid_rows_are_populated(self):
        p = mas.MASConsolidatedPriceList.load_from_upload(
            uploaded_xlsx_file(MAS_XLSX_PATH))
        self.assertEqual(len(p.valid_rows), 1)
        try:
            self.assertEqual(len(p.invalid_rows), 1)
        except Exception:
            print("invalid row found")
        self.assertEqual(p.valid_rows[0].cleaned_data, {
            'education_level': 'Bachelors',
            'labor_category': 'Principal Consultant',
            'min_years_experience': 10,
            'price_including_iff': Decimal('200.00'),
            'sin': '874-1',
            'unit_of_issue': 'Hour',
            'keywords': 'Process improvement, finance, senior project manager',
            'certifications': 'PMP',
            'security_clearance': 'No'
        })

    def test_education_level_is_validated(self):
        p = mas.MASConsolidatedPriceList(rows=[{'education_level': 'Bachelors'}])
        if 'education_level' in p.invalid_rows[0].errors.keys():
            self.assertRegexpMatches(
                p.invalid_rows[0].errors['education_level'][0],
                r'This field must contain one of the following values'
            )

    def test_price_including_iff_is_validated(self):
        p = mas.MASConsolidatedPriceList(rows=[{'price_including_iff': '1.10'}])
        self.assertRegexpMatches(
            p.invalid_rows[0].errors['price_including_iff'][0],
            r'Price must be at least'
        )

    def test_min_years_experience_is_validated(self):
        p = mas.MASConsolidatedPriceList(rows=[{'min_years_experience': ''}])

        self.assertEqual(p.invalid_rows[0].errors['min_years_experience'],
                         ['This field is required.'])

    def test_unit_of_issue_is_validated(self):
        p = mas.MASConsolidatedPriceList(rows=[{'unit_of_issue': ''}])
        if 'unit_of_issue' in p.invalid_rows[0].errors.keys():
            self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                             ['This field is required.'])

        p = mas.MASConsolidatedPriceList(rows=[{'unit_of_issue': 'Day'}])
        self.assertEqual(p.invalid_rows[0].errors['unit_of_issue'],
                         ['Value must be "Hour" or "Hourly"'])

    def test_unit_of_issue_can_be_hour_or_hourly(self):
        p = mas.MASConsolidatedPriceList(rows=[{'unit_of_issue': 'Hour'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

        p = mas.MASConsolidatedPriceList(rows=[{'unit_of_issue': 'hourly'}])
        self.assertNotIn('unit_of_issue', p.invalid_rows[0])

    def test_add_to_price_list_works(self):
        s = mas.MASConsolidatedPriceList.load_from_upload(
            uploaded_xlsx_file(MAS_XLSX_PATH))

        p = self.create_price_list()
        p.save()

        s.add_to_price_list(p)

        row = p.rows.all()[0]
        self.assertEqual(row.labor_category, 'Principal Consultant')
        self.assertEqual(row.education_level, 'BA')
        self.assertEqual(row.min_years_experience, 10)
        self.assertEqual(row.base_year_rate, Decimal('200.00'))
        self.assertEqual(row.sin, '874-1')
        self.assertEqual(row.keywords, 'Process improvement, finance, senior project manager')
        self.assertEqual(row.certifications, 'PMP')

        row.full_clean()

    def test_serialize_and_deserialize_work(self):
        s = mas.MASConsolidatedPriceList.load_from_upload(
            uploaded_xlsx_file(MAS_XLSX_PATH))

        saved = json.dumps(registry.serialize(s))
        restored = registry.deserialize(json.loads(saved))
        self.assertTrue(isinstance(restored, mas.MASConsolidatedPriceList))
        self.assertEqual(s.rows, restored.rows)

    def test_to_table_works(self):
        s = mas.MASConsolidatedPriceList.load_from_upload(
            uploaded_xlsx_file(MAS_XLSX_PATH))
        table_html = s.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_to_error_table_works(self):
        s = mas.MASConsolidatedPriceList.load_from_upload(
            uploaded_xlsx_file(MAS_XLSX_PATH))
        table_html = s.to_error_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_render_upload_example_works(self):
        html = mas.MASConsolidatedPriceList.render_upload_example()
        for row in mas.EXAMPLE_SHEET_ROWS:
            for col in row:
                self.assertIn(html_module.escape(col), html)
