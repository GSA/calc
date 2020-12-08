import io
import unittest.mock as mock
from django.conf import settings
from django.core.management import call_command
from django.contrib import messages
from django.contrib.auth.models import User
from django.test import override_settings, TestCase
from django.contrib.admin.sites import AdminSite
from django.core.files.uploadedfile import SimpleUploadedFile

from calc.tests.common import BaseLoginTestCase
from .. import admin, email
from ..models import (SubmittedPriceList, SubmittedPriceListRow,
                      AttemptedPriceListSubmission)
from .common import FAKE_SCHEDULE
from .test_models import ModelTestCase


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
)
class AdminTestCase(ModelTestCase):
    def setUp(self):
        super().setUp()
        self.price_list = self.create_price_list()
        self.price_list.save()
        self.row = self.create_row(price_list=self.price_list)
        self.row.save()

    def setup_user(self):
        call_command('initgroups', stdout=io.StringIO())
        self.user = self.login(
            is_staff=True,
            groups=('Data Administrators',)
        )


DEBUG_ADMIN_SETTINGS = dict(
    # Strangely, disabling DEBUG mode silences some errors in Django
    # admin views, so we'll enforce it so that any errors are raised.
    DEBUG=True,
    # And enabling DEBUG will enable the Django Debug Toolbar, which
    # unfortunately massively slows down our tests, so let's disable that.
    INSTALLED_APPS=tuple([
        name for name in settings.INSTALLED_APPS
        if name != 'debug_toolbar'
    ]),
    MIDDLEWARE_CLASSES=tuple([
        name for name in settings.MIDDLEWARE_CLASSES
        if name != 'calc.middleware.DebugOnlyDebugToolbarMiddleware'
    ]),
)


@override_settings(**DEBUG_ADMIN_SETTINGS)
class DebugAdminTestCase(AdminTestCase):
    pass


class CustomUserCreationFormTests(TestCase):
    def test_checks_uniqueness_of_email(self):
        User.objects.create_user(username='blerg', email='foo@gsa.gov')
        form = admin.CustomUserCreationForm({'email': 'foo@gsa.gov'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['That email address is already in use.']
        })

    def test_checks_case_insensitive_uniqueness_of_email(self):
        User.objects.create_user(username='blerg', email='foo@gsa.gov')
        form = admin.CustomUserCreationForm({'email': 'FOO@gsa.gov'})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            'email': ['That email address is already in use.']
        })

    def test_generate_username_works(self):
        form = admin.CustomUserCreationForm()
        self.assertEqual(form.generate_username('boop.jones@gsa.gov'),
                         'boopjones')

    def test_generate_username_appends_number_when_needed(self):
        User.objects.create_user(username='boopjones')
        form = admin.CustomUserCreationForm()
        self.assertEqual(form.generate_username('boop.jones@gsa.gov'),
                         'boopjones1')

    def test_generate_username_raises_exception_when_attempts_maxed_out(self):
        User.objects.create_user(username='boopjones')
        User.objects.create_user(username='boopjones1')
        form = admin.CustomUserCreationForm()
        with self.assertRaisesRegexp(
            Exception,
            'unable to generate username for '
            'boop.jones@gsa.gov after 2 attempts'
        ):
            form.generate_username('boop.jones@gsa.gov', max_attempts=2)

    def test_save_sets_username(self):
        form = admin.CustomUserCreationForm({'email': 'foo@gsa.gov'})
        self.assertTrue(form.is_valid())
        user = form.save()
        self.assertEqual(user.username, 'foo')
        self.assertEqual(user.email, 'foo@gsa.gov')


class SuperuserViewTests(DebugAdminTestCase):
    def setup_user(self):
        self.user = self.login(is_superuser=True)

    def test_can_set_superuser(self):
        res = self.client.get(
            '/admin/auth/user/{}/change/'.format(self.user.id))
        self.assertContains(res, 'Superuser')
        self.assertEqual(res.status_code, 200)

    def test_can_see_superusers(self):
        self.create_user(username='superdawg', email="superdawg@super.dawg",
                         is_superuser=True)
        res = self.client.get('/admin/auth/user/')
        self.assertContains(res, 'superdawg@super.dawg')
        self.assertEqual(res.status_code, 200)


class NonSuperuserViewTests(DebugAdminTestCase):
    '''
    Tests that non-super user Data Administrator users can access
    relevant admin views. For changes to group permissions, see initgroups.py
    '''
    def test_user_add_returns_200(self):
        res = self.client.get('/admin/auth/user/add/')
        self.assertContains(res, 'First, enter an email address',
                            status_code=200)

    def test_cannot_set_superuser(self):
        res = self.client.get(
            '/admin/auth/user/{}/change/'.format(self.user.id))
        self.assertNotContains(res, 'Superuser')
        self.assertEqual(res.status_code, 200)

    def test_cannot_see_superusers(self):
        self.create_user(username='superdawg', is_superuser=True)
        res = self.client.get('/admin/auth/user/')
        self.assertNotContains(res, 'superdawg')
        self.assertEqual(res.status_code, 200)

    def test_submittedpricelistrow_list_returns_200(self):
        res = self.client.get('/admin/data_capture/submittedpricelistrow/')
        self.assertEqual(res.status_code, 200)

    def test_unreviewed_pricelist_list_returns_200(self):
        res = self.client.get('/admin/data_capture/unreviewedpricelist/')
        self.assertEqual(res.status_code, 200)

    def test_approved_pricelist_list_returns_200(self):
        res = self.client.get(
            '/admin/data_capture/approvedpricelist/')
        self.assertEqual(res.status_code, 200)

    def test_retired_pricelist_list_returns_200(self):
        res = self.client.get(
            '/admin/data_capture/retiredpricelist/')
        self.assertEqual(res.status_code, 200)

    def test_rejected_pricelist_list_returns_200(self):
        res = self.client.get(
            '/admin/data_capture/rejectedpricelist/')
        self.assertEqual(res.status_code, 200)

    def test_unreviewed_pricelist_detail_returns_200(self):
        res = self.client.get(
            '/admin/data_capture/unreviewedpricelist/{}/change/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_retired_pricelist_detail_returns_200(self):
        self.price_list.retire(self.user)
        res = self.client.get(
            '/admin/data_capture/retiredpricelist/{}/change/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_approved_pricelist_detail_returns_200(self):
        self.price_list.approve(self.user)
        res = self.client.get(
            '/admin/data_capture/approvedpricelist/{}/change/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)

    def test_rejected_pricelist_detail_returns_200(self):
        self.price_list.reject(self.user)
        res = self.client.get(
            '/admin/data_capture/rejectedpricelist/{}/change/'.format(
                self.price_list.id
            )
        )
        self.assertEqual(res.status_code, 200)


@mock.patch.object(messages, 'add_message')
class ActionTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.request_mock = mock.MagicMock(user=self.user)

    def test_approve_ignores_approved_price_lists(self, mock):
        self.price_list.approve(self.user)
        admin.approve(None, self.request_mock,
                      SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            self.request_mock,
            messages.INFO,
            '0 price list(s) have been approved and added to CALC.'
        )

    def test_retire_ignores_retired_price_lists(self, mock):
        admin.retire(None, self.request_mock,
                     SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            self.request_mock,
            messages.INFO,
            '0 price list(s) have been retired and removed from CALC.'
        )

    def test_reject_ignores_rejected_price_lists(self, mock):
        self.price_list.reject(self.user)
        admin.reject(None, self.request_mock, SubmittedPriceList.objects.all())
        mock.assert_called_once_with(
            self.request_mock,
            messages.INFO,
            '0 price list(s) have been rejected.'
        )

    def test_approve_works(self, msg_mock):
        with mock.patch.object(email, 'price_list_approved',
                               wraps=email.price_list_approved) as em_monkey:
            admin.approve(None, self.request_mock,
                          SubmittedPriceList.objects.all())
            msg_mock.assert_called_once_with(
                self.request_mock,
                messages.INFO,
                '1 price list(s) have been approved and added to CALC.'
            )
            em_monkey.assert_called_once_with(self.price_list)

        self.price_list.refresh_from_db()
        self.assertEqual(self.price_list.status,
                         SubmittedPriceList.STATUS_APPROVED)

    def test_retire_works(self, msg_mock):
        with mock.patch.object(email, 'price_list_retired',
                               wraps=email.price_list_retired) as em_monkey:
            self.price_list.approve(self.user)

            admin.retire(None, self.request_mock,
                         SubmittedPriceList.objects.all())
            msg_mock.assert_called_once_with(
                self.request_mock,
                messages.INFO,
                '1 price list(s) have been retired and removed from CALC.'
            )
            em_monkey.assert_called_once_with(self.price_list)

        self.price_list.refresh_from_db()
        self.assertEqual(self.price_list.status,
                         SubmittedPriceList.STATUS_RETIRED)

    def test_reject_works(self, msg_mock):
        with mock.patch.object(email, 'price_list_rejected',
                               wraps=email.price_list_rejected) as em_monkey:
            admin.reject(None, self.request_mock,
                         SubmittedPriceList.objects.all())
            msg_mock.assert_called_once_with(
                self.request_mock,
                messages.INFO,
                '1 price list(s) have been rejected.'
            )
            em_monkey.assert_called_once_with(self.price_list)
        self.price_list.refresh_from_db()
        self.assertEqual(self.price_list.status,
                         SubmittedPriceList.STATUS_REJECTED)


class SubmittedPriceListRowAdminTests(AdminTestCase):
    def setUp(self):
        super().setUp()
        self.site = AdminSite()
        self.pl_model_admin = admin.SubmittedPriceListRowAdmin(
            SubmittedPriceListRow, self.site)

    def test_contract_number_link_works(self):
        for val, label in SubmittedPriceList.STATUS_CHOICES:
            self.price_list.status = val
            self.assertEqual(
                self.pl_model_admin.contract_number(self.row),
                '<a href="/admin/data_capture/{}pricelist/{}/change/">{}</a>'.format(  # NOQA
                    label,
                    self.price_list.id,
                    self.price_list.contract_number)
            )

    def test_vendor_name_works(self):
        self.assertEqual(
            self.price_list.vendor_name,
            self.pl_model_admin.vendor_name(self.row))

    def test_has_add_permission_is_false(self):
        self.assertFalse(self.pl_model_admin.has_add_permission(self.row))


@override_settings(**DEBUG_ADMIN_SETTINGS)
class AttemptedPriceListSubmissionAdminTests(BaseLoginTestCase):
    URL_PREFIX = '/admin/data_capture/attemptedpricelistsubmission/'

    def setUp(self):
        super().setUp()
        call_command('initgroups', stdout=io.StringIO())
        self.user = self.create_user(
            username='foo', is_staff=True, email='foo@example.org',
            groups=['Technical Support Specialists'])
        self.apls = AttemptedPriceListSubmission(
            submitter=self.user,
            session_state='{}'
        )
        f = SimpleUploadedFile(name='blah.csv', content=b'blah,meh')
        self.apls.set_uploaded_file(f)
        self.apls.save()

    def assert_403(self, url):
        self.assertEqual(self.client.get(url).status_code, 403)

    def test_views_are_protected_from_non_tech_support_folks(self):
        self.login(username='bar', is_staff=True)
        self.assert_403(f'{self.URL_PREFIX}')
        self.assert_403(f'{self.URL_PREFIX}{self.apls.id}/change/')
        self.assert_403(f'{self.URL_PREFIX}{self.apls.id}/download/')

    def test_view_works(self):
        self.client.force_login(self.user)
        res = self.client.get(f'{self.URL_PREFIX}{self.apls.id}/change/')
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'blah.csv')

    def test_download_works(self):
        self.client.force_login(self.user)
        res = self.client.get(f'{self.URL_PREFIX}{self.apls.id}/download/')
        self.assertEqual(res.status_code, 200)
        self.assertEqual(
            res['Content-Disposition'],
            'attachment; filename="blah.csv"')
        self.assertEqual(
            res['Content-Type'],
            'application/octet-stream')
        self.assertEqual(res.content, b'blah,meh')
