import json
import unittest.mock as mock
from datetime import datetime, date

from freezegun import freeze_time
from model_mommy import mommy
from django.test import override_settings
from django.utils import timezone

from calc.tests.common import ProtectedViewTestCase
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import FAKE_SCHEDULE, uploaded_csv_file
from ..schedules import registry


frozen_datetime = datetime(2016, 2, 11, 15, 20, 31)


class ListViewTests(ProtectedViewTestCase):
    url = '/data-capture/price-lists'

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('approved_price_lists', ctx)
        self.assertIn('unreviewed_price_lists', ctx)
        self.assertIn('rejected_price_lists', ctx)
        self.assertIn('retired_price_lists', ctx)

    def test_only_includes_price_lists_for_user(self):
        user = self.login()
        other_user = self.create_user('other_user')

        for val, label in SubmittedPriceList.STATUS_CHOICES:
            mommy.make(SubmittedPriceList,
                       submitter=user,
                       status=val)

            mommy.make(SubmittedPriceList,
                       submitter=other_user,
                       status=val)

        res = self.client.get(self.url)
        ctx = res.context
        self.assertEqual(len(ctx['approved_price_lists']), 1)
        self.assertEqual(len(ctx['unreviewed_price_lists']), 1)
        self.assertEqual(len(ctx['rejected_price_lists']), 1)
        self.assertEqual(len(ctx['retired_price_lists']), 1)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class DetailsViewTests(ProtectedViewTestCase):
    url = '/data-capture/price-lists/'

    valid_post_data = {
        'vendor_name': "Hansen's Hotcakes",
        'is_small_business': 'False',
        'contractor_site': 'Customer',
        'escalation_rate': '0',
        'contract_start_0': '1985',
        'contract_start_1': '07',
        'contract_start_2': '08',
        'contract_end_0': '1989',
        'contract_end_1': '04',
        'contract_end_2': '14',
    }

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def setUp(self):
        super().setUp()
        a_user = self.create_user('a_user')
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        serialized = registry.serialize(p)
        self.price_list = mommy.make(
            SubmittedPriceList,
            schedule=FAKE_SCHEDULE,
            submitter=a_user,
            contract_number="GS-12-1234",
            serialized_gleaned_data=json.dumps(serialized),
            created_at=timezone.now(),
            is_small_business=True,
            contractor_site='Both',
            escalation_rate=1.2,
            contract_start=date(2016, 2, 11),
            contract_end=date(2020, 2, 11),
            status=SubmittedPriceList.STATUS_UNREVIEWED)
        self.url += str(self.price_list.pk)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertFalse(res.context['show_edit_form'])

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('price_list', ctx)
        self.assertIn('gleaned_data', ctx)
        self.assertEqual(ctx['price_list'], self.price_list)

    @freeze_time(frozen_datetime)
    def test_post_updates_price_list(self):
        user = self.login()
        res = self.client.post(self.url, self.valid_post_data, follow=True)
        self.assertRedirects(res, self.url)
        self.assertEqual(res.status_code, 200)
        self.assertHasMessage(
            res,
            'success',
            "Your changes have been submitted. An administrator will "
            "review them before they are live in CALC.")

        pl = SubmittedPriceList.objects.get(id=self.price_list.pk)
        self.assertEqual(pl.status_changed_by, user)
        self.assertEqual(pl.status, SubmittedPriceList.STATUS_UNREVIEWED)
        self.assertEqual(
            pl.status_changed_at,
            timezone.make_aware(frozen_datetime))
        self.assertEqual(pl.submitter, user)
        self.assertEqual(pl.vendor_name, self.valid_post_data['vendor_name'])
        self.assertEqual(pl.is_small_business, False)
        self.assertEqual(pl.contractor_site,
                         self.valid_post_data['contractor_site'])
        self.assertEqual(pl.contract_start, date(1985, 7, 8))
        self.assertEqual(pl.contract_end, date(1989, 4, 14))
        self.assertEqual(pl.escalation_rate, 0)

    @mock.patch.object(SubmittedPriceList, 'unreview')
    def test_valid_post_calls_unreview(self, mock):
        self.login()
        res = self.client.post(self.url, self.valid_post_data, follow=True)
        self.assertRedirects(res, self.url)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(mock.call_count, 1)

    def test_invalid_post_shows_errors(self):
        self.login()
        data = self.valid_post_data.copy()
        data['contractor_site'] = 'LOL'
        res = self.client.post(self.url, data)
        self.assertTrue(res.context['show_edit_form'], True)
        self.assertContains(res, 'LOL is not one of the available choices')

    def test_post_of_unchanged_data_shows_message(self):
        self.login()
        pl = SubmittedPriceList.objects.get(id=self.price_list.pk)
        data = {
            'vendor_name': pl.vendor_name,
            'is_small_business': pl.is_small_business,
            'contractor_site': pl.contractor_site,
            'escalation_rate': pl.escalation_rate,
            'contract_start_0': pl.contract_start.year,
            'contract_start_1': pl.contract_start.month,
            'contract_start_2': pl.contract_start.day,
            'contract_end_0': pl.contract_end.year,
            'contract_end_1': pl.contract_end.month,
            'contract_end_2': pl.contract_end.day,
        }
        res = self.client.post(self.url, data, follow=True)
        self.assertRedirects(res, self.url)
        self.assertHasMessage(
            res,
            'info',
            "This price list has not been modified because no changes "
            "were found in the submitted form."
        )
