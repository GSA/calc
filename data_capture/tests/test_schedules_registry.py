from unittest.mock import patch
from django.test import TestCase, override_settings
from django.core.exceptions import ValidationError

from ..schedules import registry
from ..schedules.registry import smart_load_from_upload
from ..schedules.base import BasePriceList
from ..schedules.fake_schedule import FakeSchedulePriceList
from .common import FAKE_SCHEDULE, uploaded_csv_file, create_csv_content


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class FakeScheduleOnlyTests(TestCase):
    def test_get_choices_works(self):
        self.assertEqual(
            [choice for choice in registry.get_choices()],
            [(FAKE_SCHEDULE, FakeSchedulePriceList.title)]
        )

    def test_get_class_works(self):
        self.assertEqual(registry.get_class(FAKE_SCHEDULE),
                         FakeSchedulePriceList)

    def test_get_classname_works(self):
        p = FakeSchedulePriceList([])
        self.assertEqual(registry.get_classname(p), FAKE_SCHEDULE)

    def test_load_from_upload_works(self):
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        self.assertTrue(isinstance(p, FakeSchedulePriceList))
        self.assertFalse(p.is_empty())

    def test_serialize_and_deserialize_work(self):
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        serialized = registry.serialize(p)
        deserialized = registry.deserialize(serialized)
        self.assertEqual(p.rows, deserialized.rows)

    def test_to_table_works(self):
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        table_html = p.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))

    def test_to_table_renders_price_correctly(self):
        p = registry.load_from_upload(
            FAKE_SCHEDULE,
            uploaded_csv_file(content=create_csv_content(rows=[
                ['132-40', 'Project Manager', 'High School', '7', '25.8989']
            ])))
        table_html = p.to_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))
        self.assertNotIn('25.8989', table_html)
        self.assertIn('$25.90', table_html)

    def test_to_error_table_works(self):
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        table_html = p.to_error_table()
        self.assertIsNotNone(table_html)
        self.assertTrue(isinstance(table_html, str))


class FooSchedulePriceList(BasePriceList):
    title = 'Foo Schedule'

    @classmethod
    def load_from_upload(cls, f):
        f.read()
        raise ValidationError('Bar')


FOO_SCHEDULE = '%s.FooSchedulePriceList' % __name__


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE, FOO_SCHEDULE])
class FooScheduleTests(TestCase):
    def test_get_choices_works(self):
        self.assertEqual(
            [choice for choice in registry.get_choices()],
            [(FAKE_SCHEDULE, FakeSchedulePriceList.title),
             (FOO_SCHEDULE, 'Foo Schedule')]
        )


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE, FOO_SCHEDULE])
class SmartLoadFromUploadTests(TestCase):
    def test_better_matches_are_found(self):
        p = smart_load_from_upload(FOO_SCHEDULE, uploaded_csv_file())
        self.assertTrue(isinstance(p, FakeSchedulePriceList))

    @patch.object(FooSchedulePriceList, 'load_from_upload')
    def test_others_not_consulted_when_preferred_schedule_matches(self, m):
        p = smart_load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        self.assertEqual(m.call_count, 0)
        self.assertTrue(isinstance(p, FakeSchedulePriceList))

    def test_original_error_propagated_when_better_matches_not_found(self):
        with self.assertRaisesRegexp(ValidationError, 'Bar'):
            smart_load_from_upload(FOO_SCHEDULE, uploaded_csv_file(b'nope'))
