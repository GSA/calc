from django.test import TestCase

import xlrd

from .common import r10_file
from ..r10_spreadsheet_converter import Region10SpreadsheetConverter

expected_results = [
    ['Project Manager', '123.466', '134.3844', '145.6253', '156.1946', '165.0981', 'Bachelors', '8.0', 'S', 'Both', 'Acme, LLC', 'GS-12F-0123S', 'MOBIS', '123-1, 123-1RC, 456-7, 456-7RC', '2.0', '06/01/2006', '05/31/2021'],  # NOQA
    ['BAD ROW', '', '', '', '', '', '', '', '', '', '', '', '', '', '', '', ''],  # NOQA
    ['Software Developer', '100.0', '101.0', '102.0', '103.0', '104.0', 'Masters', '5.0', 'S', 'Both', 'Foobar Inc', 'GS-12F-0456S', 'MOBIS', '123-2, 456-8', '3.0', '05/01/2010', '05/31/2021'],  # NOQA
    ['QA Engineer', '75.1', '85.2', '95.3', '105.4', '115.5', 'Associates', '2.0', 'O', 'Both', 'Boop Associates', 'GS-12F-0789S', 'MOBIS', '123-3', '1.0', '07/01/2016', '05/31/2021'],  # NOQA
]


class TestRegion10SpreadsheetConverter(TestCase):
    '''Tests for Region10SpreadsheetConverter'''

    def test_is_valid_file(self):
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        self.assertTrue(converter.is_valid_file())

        converter.xl_heading_to_csv_idx_map = {'Location': 0}
        self.assertTrue(converter.is_valid_file())

        converter.xl_heading_to_csv_idx_map = {'bad_col': 0}
        self.assertFalse(converter.is_valid_file())

        converter = Region10SpreadsheetConverter(xls_file=r10_file('blah'))
        self.assertFalse(converter.is_valid_file())

    def test_get_metadata(self):
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        book = xlrd.open_workbook(file_contents=r10_file().read())
        sheet = book.sheet_by_index(0)
        expected = {
            'num_rows': sheet.nrows - 1
        }
        self.assertEqual(expected, converter.get_metadata())

    def test_get_heading_indices_map(self):
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        indices_map = converter.get_heading_indices_map()

        expected = {
            'Year 1/base': 1,
            'Contract Year': 17,
            'CONTRACT .': 11,
            'Year 3': 3,
            'Schedule': 12,
            'MinExpAct': 7,
            'Location': 9,
            'Begin Date': 14,
            'COMPANY NAME': 10,
            'SIN NUMBER': 13,
            'Labor Category': 0,
            'Year 2': 2,
            'Year 5': 5,
            'Education': 6,
            'End Date': 15,
            'Year 4': 4,
            'Bus Size': 8
        }
        self.assertEqual(expected, indices_map)

    def test_get_heading_indices_map_raises(self):
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        converter.xl_heading_to_csv_idx_map = {'blah': 0, 'boop': 1}
        with self.assertRaises(ValueError) as cm:
            converter.get_heading_indices_map(raises=True)
            self.assertIn('Missing columns', cm.exception)
            self.assertIn('blah', cm.exception)
            self.assertIn('boop', cm.exception)

    def test_convert_next(self):
        count = 0
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        for row in converter.convert_next():
            self.assertEqual(expected_results[count], row)
            count += 1

        self.assertEqual(count, 4)

    def test_convert_file(self):
        converter = Region10SpreadsheetConverter(xls_file=r10_file())
        parsed_rows = converter.convert_file()
        self.assertEqual(len(parsed_rows), 4)
        self.assertEqual(expected_results, parsed_rows)
