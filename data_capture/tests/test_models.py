from datetime import datetime, date
from decimal import Decimal
from unittest.mock import patch

from freezegun import freeze_time
from django.test import override_settings, TestCase
from django.utils import timezone
from django.forms import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from calc.tests.common import BaseLoginTestCase
from contracts.models import Contract
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..models import (SubmittedPriceList, SubmittedPriceListRow,
                      HashedUploadedFile)
from .common import FAKE_SCHEDULE


frozen_datetime = datetime(2017, 1, 12, 9, 15, 20)


class HashedUploadedFileTests(TestCase):
    UPLOAD_DIR = 'data_capture_uploaded_files'

    def test_store_creates_files(self):
        f = SimpleUploadedFile(name='blah.txt', content=b'blah')
        uf = HashedUploadedFile.store(f)
        self.assertEqual(
            uf.hex_hash,
            '8b7df143d91c716ecfa5fc1730022f6b421b05cedee8fd52b1fc65a96030ad52'
        )
        self.assertEqual(uf.contents.read(), b'blah')
        self.assertEqual(uf.contents.size, 4)
        self.assertIn(self.UPLOAD_DIR, uf.contents.name)
        self.assertIn('blah', uf.contents.name)

    def test_store_returns_existing_files(self):
        uf1 = HashedUploadedFile.store(SimpleUploadedFile(
            name='f1', content=b'zz'))
        uf2 = HashedUploadedFile.store(SimpleUploadedFile(
            name='f2', content=b'zz'))
        self.assertEqual(uf1, uf2)
        self.assertEqual(HashedUploadedFile.objects.all().count(), 1)

    def test_store_saves_different_files_with_same_name(self):
        uf1 = HashedUploadedFile.store(
            SimpleUploadedFile(name='zz', content=b'a'))
        uf2 = HashedUploadedFile.store(
            SimpleUploadedFile(name='zz', content=b'b'))
        self.assertIn('zz', uf1.contents.name)
        self.assertIn('zz', uf2.contents.name)
        self.assertNotEqual(uf1.contents.name, uf2.contents.name)


class ModelTestCase(BaseLoginTestCase):
    DEFAULT_SCHEDULE = FAKE_SCHEDULE

    def setUp(self):
        super().setUp()
        self.setup_user()

    def setup_user(self):
        self.user = self.create_user(username='foo', email='foo@example.com')

    def create_price_list(self, **kwargs):
        final_kwargs = dict(
            submitter=self.user,
            is_small_business=False,
            contract_number='GS-123-4567',
            vendor_name='UltraCorp',
            schedule=self.DEFAULT_SCHEDULE,
            contract_start=date(2016, 9, 1),
            contract_end=date(2021, 9, 1),
            escalation_rate=0,
            status=SubmittedPriceList.STATUS_UNREVIEWED,
            status_changed_by=self.user,
            status_changed_at=timezone.now(),
        )
        final_kwargs.update(kwargs)
        return SubmittedPriceList(**final_kwargs)

    def create_row(self, **kwargs):
        final_kwargs = dict(
            labor_category='Project Manager',
            min_years_experience=5,
            base_year_rate=10,
        )
        final_kwargs.update(kwargs)
        return SubmittedPriceListRow(**final_kwargs)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class ModelsTests(ModelTestCase):
    def test_add_row_works(self):
        p = self.create_price_list()
        p.save()
        row = p.add_row(
            labor_category='Project Manager',
            min_years_experience=5,
            base_year_rate=10,
        )
        self.assertEqual(list(p.rows.all()), [row])
        self.assertEqual(row.labor_category, 'Project Manager')
        self.assertEqual(row.min_years_experience, 5)
        self.assertEqual(row.base_year_rate, 10)

    def test_get_schedule_title_works(self):
        p = self.create_price_list(schedule=FAKE_SCHEDULE)
        self.assertEqual(p.get_schedule_title(),
                         FakeSchedulePriceList.title)

    def test_get_business_size_string_works(self):
        p = self.create_price_list(is_small_business=False)
        self.assertEqual(p.get_business_size_string(), 'O')

        p.is_small_business = True
        self.assertEqual(p.get_business_size_string(), 'S')

    @freeze_time(frozen_datetime)
    @patch('data_capture.models.logger')
    def test_change_status_works(self, mock_logger):
        original_user = self.create_user(username='boop', email="boop@beep")
        p = self.create_price_list(
            pk=5,
            status=SubmittedPriceList.STATUS_UNREVIEWED,
            status_changed_by=original_user)
        p._change_status(SubmittedPriceList.STATUS_APPROVED, self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_APPROVED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(
            p.status_changed_at,
            timezone.make_aware(frozen_datetime))
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(
            mock_logger.info.call_args[0][0],
            f'Price list with id 5 has been set to approved by user id '
            f'{self.user.id} ({self.user.email})')

    @freeze_time(frozen_datetime)
    @patch('data_capture.models.logger')
    def test_approve_works(self, mock_logger):
        p = self.create_price_list(
            pk=5,
            contract_number='GS-123-4568',
            schedule=FAKE_SCHEDULE,
            escalation_rate=1
        )
        p.save()
        row = self.create_row(labor_category='Software Engineer',
                              price_list=p)
        row.save()
        self.create_row(price_list=p, is_muted=True).save()
        p.approve(self.user)

        self.assertEqual(Contract.objects.all().count(), 1)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_APPROVED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(
            mock_logger.info.call_args[0][0],
            f'Price list with id 5 has been set to approved by user id '
            f'{self.user.id} ({self.user.email})')

        contract = p.rows.all()[0].contract_model
        self.assertEqual(contract.idv_piid, 'GS-123-4568')
        self.assertEqual(contract.labor_category, 'Software Engineer')
        self.assertEqual(contract.schedule, FakeSchedulePriceList.title)
        self.assertEqual(contract.labor_category, 'Software Engineer')
        self.assertEqual(contract.hourly_rate_year1, Decimal(10.00))
        self.assertAlmostEqual(
            contract.hourly_rate_year2, Decimal(10.10), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year3, Decimal(10.20), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year4, Decimal(10.30), places=2)
        self.assertAlmostEqual(
            contract.hourly_rate_year5, Decimal(10.41), places=2)
        self.assertEqual(contract.contract_year, 1)
        self.assertEqual(contract.current_price, 10.00)
        self.assertAlmostEqual(
            contract.next_year_price, Decimal(10.10), places=2)
        self.assertAlmostEqual(
            contract.second_year_price, Decimal(10.20), places=2)

    @freeze_time(frozen_datetime)
    @patch('data_capture.models.logger')
    def test_retire_works(self, mock_logger):
        p = self.create_price_list(pk=5)
        p.save()
        self.create_row(price_list=p).save()
        self.create_row(price_list=p, is_muted=True).save()
        p.approve(self.user)
        p.retire(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_RETIRED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(
            mock_logger.info.call_args[0][0],
            f'Price list with id 5 has been set to retired by user id '
            f'{self.user.id} ({self.user.email})')

    @freeze_time(frozen_datetime)
    @patch('data_capture.models.logger')
    def test_reject_works(self, mock_logger):
        p = self.create_price_list(pk=5)
        p.save()
        self.create_row(price_list=p).save()
        p.reject(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_REJECTED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(
            mock_logger.info.call_args[0][0],
            f'Price list with id 5 has been set to rejected by user id '
            f'{self.user.id} ({self.user.email})')

    def test_reject_raises_when_not_STATUS_UNREVIEWED(self):
        p = self.create_price_list()
        p.save()
        self.create_row(price_list=p).save()
        p.approve(self.user)
        with self.assertRaises(AssertionError):
            p.reject(self.user)

    @freeze_time(frozen_datetime)
    @patch('data_capture.models.logger')
    def test_unreview_works(self, mock_logger):
        p = self.create_price_list(pk=5)
        p.save()
        self.create_row(price_list=p).save()
        p.approve(self.user)
        p.unreview(self.user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_UNREVIEWED)
        self.assertEqual(p.status_changed_by, self.user)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.rows.all()[0].contract_model, None)
        self.assertEqual(Contract.objects.all().count(), 0)
        self.assertTrue(mock_logger.info.called)
        self.assertEqual(
            mock_logger.info.call_args[0][0],
            f'Price list with id 5 has been set to unreviewed by user id '
            f'{self.user.id} ({self.user.email})')

    def test_row_stringify_works(self):
        self.assertEqual(str(self.create_row()), 'Submitted price list row')

    def test_get_latest_by_contract_number_works(self):
        p1 = self.create_price_list()
        p1.save()

        p2 = self.create_price_list()
        p2.save()

        latest = SubmittedPriceList.get_latest_by_contract_number(
            'GS-123-4567')
        self.assertEqual(p2, latest)

    def test_get_latest_by_contract_number_ignores_case(self):
        p = self.create_price_list(contract_number='GS-AA-bbbb')
        p.save()
        latest = SubmittedPriceList.get_latest_by_contract_number(
            'gs-AA-bbBB')
        self.assertEqual(p, latest)

    def test_contract_number_is_validated(self):
        p = self.create_price_list(contract_number='***GS-123-3456')
        with self.assertRaises(ValidationError) as cm:
            p.full_clean()
            self.assertIn('Please use only letters, numbers, and dashes (-).',
                          cm.exception)
