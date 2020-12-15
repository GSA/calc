import copy
import re

from unittest.mock import Mock, MagicMock
from django.test import SimpleTestCase as TestCase
from django.core.exceptions import ValidationError

from ..schedules.spreadsheet_utils import (
    generate_column_index_map, safe_cell_str_value, ColumnTitle)


class SafeCellStrValueTests(TestCase):
    def test_cell_value_index_errors_are_ignored(self):
        s = MagicMock()
        s.cell_value.side_effect = IndexError()

        self.assertEqual(safe_cell_str_value(s, 99, 99), '')
        self.assertEqual(s.cell_value.call_count, 1)

    def test_coercer_value_errors_are_ignored(self):
        s = MagicMock()
        s.cell_value.return_value = 'blah'

        c = Mock()
        c.side_effect = ValueError()

        self.assertEqual(safe_cell_str_value(s, 99, 99, c), 'blah')
        self.assertEqual(s.cell_value.call_count, 1)
        self.assertEqual(c.call_count, 1)

    def test_result_is_stringified(self):
        s = MagicMock()
        s.cell_value.return_value = 5

        self.assertEqual(safe_cell_str_value(s, 1, 1), '5')

    def test_coercer_is_used(self):
        s = MagicMock()
        s.cell_value.return_value = 5.0

        self.assertEqual(safe_cell_str_value(s, 1, 1, int), '5')


class TestColumnTitle(TestCase):
    def test_str_alternatives_match(self):
        title = ColumnTitle('zzz', ['HEADING 3'])
        self.assertTrue(title.matches('  heading 3'))
        self.assertFalse(title.matches('  heading 4'))

    def test_regex_alternatives_match(self):
        title = ColumnTitle('zzz', [re.compile(r'BOP.*')])
        self.assertTrue(title.matches('BOPkfie'))
        self.assertFalse(title.matches('blergBOPkfie'))


class TestGenerateColumnIndexMap(TestCase):
    def setUp(self):
        self.heading_row = [
            Mock(value='HEADING 2'),
            Mock(value='heading 1'),
            Mock(value='  Heading 3  '),
        ]

        self.field_title_map = {
            'field_1': 'heading 1',
            'field_2': 'heading 2',
            'field_3': ColumnTitle('heading 3'),
        }

    def test_generate_column_index_map_works(self):
        col_idx_map = generate_column_index_map(
            self.heading_row, self.field_title_map)
        self.assertEqual(col_idx_map, {
            'field_1': 1,
            'field_2': 0,
            'field_3': 2,
        })

    def test_raises_on_missing_field(self):
        map_with_additional_field = copy.copy(self.field_title_map)
        map_with_additional_field['missing_field'] = 'BOOP'
        with self.assertRaises(ValidationError):
            generate_column_index_map(
                self.heading_row, map_with_additional_field)
