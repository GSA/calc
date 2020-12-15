import json

from datetime import datetime
from model_mommy import mommy
from django.test import override_settings
from django.core.urlresolvers import reverse
from django.utils import timezone
from freezegun import freeze_time

from .common import (StepTestCase, FAKE_SCHEDULE, uploaded_csv_file,
                     create_csv_content)
from ..schedules import registry
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from ..views.price_list_replace import SESSION_KEY


frozen_datetime = datetime(2016, 4, 23, 10, 55, 16)


class HandleCancelMixin():
    def test_cancel_clears_session_and_redirects(self):
        self.login()
        res = self.client.post(self.url, {'cancel': ''})
        self.assertRedirects(res, reverse('data_capture:price_list_details',
                             kwargs={'id': self.price_list.pk}))
        session = self.client.session
        for k in list(session.keys()):
            self.assertFalse(k.startswith(SESSION_KEY))


class RequireSessionVarsMixin():
    def test_redirects_if_session_id_is_missing(self):
        self.login()
        sess = self.client.session
        sess[SESSION_KEY] = {}
        sess.save()
        res = self.client.get(self.url)
        self.assertRedirects(res, reverse('data_capture:price_list_details',
                             kwargs={'id': self.price_list.pk}))

    def test_errors_if_session_id_is_different(self):
        self.login()
        sess = self.client.session
        sess[SESSION_KEY] = {
            'price_list_id': '999'
        }
        sess.save()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 400)


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class ReplaceStepTest(StepTestCase):
    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    def setUp(self):
        super().setUp()
        a_user = self.create_user('a_user')
        p = registry.load_from_upload(FAKE_SCHEDULE, uploaded_csv_file())
        serialized = registry.serialize(p)
        self.price_list = mommy.make(
            SubmittedPriceList,
            schedule=FAKE_SCHEDULE,
            submitter=a_user,
            contract_number='GS-12-1234',
            serialized_gleaned_data=json.dumps(serialized),
        )
        if self.url:
            self.url = self.format_url(self.url)

    def login(self, **kwargs):
        kwargs['permissions'] = [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def format_url(self, template_url, id=None):
        if not id:
            id = self.price_list.pk
        return str.replace(template_url, '<id>', str(id))

    def setup_session(self, rows, filename='bar.csv'):
        session = self.client.session
        uploaded_price_list = FakeSchedulePriceList(rows)
        session[SESSION_KEY] = {
            'gleaned_data': registry.serialize(uploaded_price_list),
            'uploaded_filename': filename,
            'price_list_id': str(self.price_list.pk),
        }
        session.save()


class ReplaceStep1Tests(ReplaceStepTest):
    url = '/data-capture/price-lists/<id>/replace/step/1'

    def ajax_post(self, data):
        res = self.client.post(self.url, data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        return res, json.loads(res.content.decode('utf-8'))

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('form', ctx)
        self.assertIn('price_list', ctx)

    def test_valid_post_sets_session_variables(self):
        self.login()
        self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        sess = self.client.session[SESSION_KEY]
        self.assertIn('gleaned_data', sess)
        self.assertIn('price_list_id', sess)
        self.assertIn('uploaded_filename', sess)
        gleaned_data = registry.deserialize(sess['gleaned_data'])
        assert isinstance(gleaned_data, FakeSchedulePriceList)
        self.assertEqual(sess['uploaded_filename'], 'foo.csv')
        self.assertEqual(sess['price_list_id'], str(self.price_list.pk))

    def test_valid_post_redirects_to_step_2(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        self.assertRedirects(
            res,
            self.format_url(ReplaceStep2Tests.url)
        )

    def test_valid_post_with_row_errors_redirects_to_step_1_errors(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertRedirects(
            res,
            self.format_url(ReplaceStep1ErrorTests.url)
        )

    def test_valid_ajax_post_returns_json(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file()
        })
        self.assertEqual(json_data, {
            'redirect_url': self.format_url(ReplaceStep2Tests.url)
        })

    def test_valid_ajax_post_with_row_errors_redirects_to_step_1_errors(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertEqual(json_data, {
            'redirect_url': self.format_url(ReplaceStep1ErrorTests.url)
        })

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, r'<!DOCTYPE html>')
        self.assertContains(res, r'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops! Please correct the following error.'
        )

    def test_invalid_ajax_post_returns_json(self):
        self.login()
        res, json_data = self.ajax_post({})
        assert '<!DOCTYPE html>' not in json_data['form_html']
        self.assertRegexpMatches(json_data['form_html'],
                                 r'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops! Please correct the following error.'
        )


class ReplaceStep1ErrorTests(ReplaceStepTest, HandleCancelMixin,
                             RequireSessionVarsMixin):
    url = '/data-capture/price-lists/<id>/replace/step/1/errors'

    def setUp(self):
        super().setUp()
        self.setup_session(self.rows)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('gleaned_data', ctx)
        self.assertIn('price_list', ctx)
        self.assertIn('form', ctx)


class ReplaceStep2Tests(ReplaceStepTest, HandleCancelMixin,
                        RequireSessionVarsMixin):
    url = '/data-capture/price-lists/<id>/replace/step/2'

    def setUp(self):
        super().setUp()
        self.setup_session(self.rows)

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_has_context_vars(self):
        self.login()
        res = self.client.get(self.url)
        ctx = res.context
        self.assertIn('gleaned_data', ctx)
        self.assertIn('price_list', ctx)

    def test_get_redirects_if_no_valid_rows(self):
        self.setup_session(rows=[])
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res,
                             reverse('data_capture:replace_step_1',
                                     kwargs={'id': self.price_list.pk}))

    def test_bad_response_if_post_with_no_valid_rows(self):
        self.setup_session(rows=[])
        self.login()
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)

    def test_valid_post_redirects_to_details_with_message(self):
        self.login()
        res = self.client.post(self.url, follow=True)
        self.assertRedirects(res,
                             reverse('data_capture:price_list_details',
                                     kwargs={'id': self.price_list.pk}))
        self.assertHasMessage(
            res,
            'success',
            "Your changes have been submitted. An administrator will "
            "review them before they are live in CALC."
        )

    @freeze_time(frozen_datetime)
    def test_valid_post_updates_model_and_clears_session(self):
        user = self.login()
        self.client.post(self.url, follow=True)
        pl = SubmittedPriceList.objects.get(pk=self.price_list.pk)
        self.assertEqual(pl, self.price_list)
        self.assertEqual(pl.submitter, user)
        self.assertEqual(pl.status, SubmittedPriceList.STATUS_UNREVIEWED)
        self.assertEqual(pl.status_changed_by, user)
        self.assertEqual(pl.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(pl.uploaded_filename, 'bar.csv')
        self.assertEqual(pl.contract_number, 'GS-12-1234')  # unchanged
        self.assertEqual(len(pl.rows.all()), len(self.rows))

        deserialized_gleaned_data = registry.deserialize(
            json.loads(pl.serialized_gleaned_data))

        self.assertEqual(deserialized_gleaned_data.rows, [{
            'education': 'Bachelors',
            'price': '15.00',
            'service': 'Project Manager',
            'sin': '132-40',
            'years_experience': '7',
        }])

        r = pl.rows.all()[0]
        self.assertEqual(r.labor_category, 'Project Manager')
        self.assertEqual(r.education_level, 'BA')
        self.assertEqual(r.min_years_experience, 7)
        self.assertEqual(r.base_year_rate, 15)
        self.assertEqual(r.sin, '132-40')

        sess = self.client.session
        self.assertNotIn(SESSION_KEY, sess)
