import json
from datetime import datetime

from model_mommy import mommy
from django.utils import timezone
from django.test import override_settings, TestCase
from freezegun import freeze_time

from ..models import SubmittedPriceList, AttemptedPriceListSubmission
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..schedules import registry
from ..management.commands.initgroups import (
    PRICE_LIST_UPLOAD_PERMISSION,
    VIEW_ATTEMPT_PERMISSION)
from .common import (StepTestCase, FAKE_SCHEDULE, uploaded_csv_file,
                     create_csv_content)


frozen_datetime = datetime(2016, 11, 16, 12, 30, 30)


class HandleCancelMixin():
    def test_cancel_clears_session_and_redirects(self):
        self.login()
        res = self.client.post(self.url, {'cancel': ''})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/')
        session = self.client.session
        for k in list(session.keys()):
            self.assertFalse(k.startswith('data_capture:'))


class RequireGleanedDataMixin():
    def test_gleaned_data_is_required(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step3Tests.url)


class PriceListStepTestCase(StepTestCase):
    # TODO: Move individual setUp functions here if applicable
    def set_fake_gleaned_data(self, rows, filename='foo.csv'):
        session = self.client.session
        pricelist = FakeSchedulePriceList(rows)
        session['data_capture:price_list']['schedule'] = \
            registry.get_classname(pricelist)
        session['data_capture:price_list']['gleaned_data'] = \
            registry.serialize(pricelist)
        session['data_capture:price_list']['filename'] = filename
        session.save()

    def delete_price_list_from_session(self):
        session = self.client.session
        del session['data_capture:price_list']
        session.save()

    def setUp(self):
        super().setUp()

    def login(self, **kwargs):
        perms = kwargs.get('permissions', [])
        kwargs['permissions'] = perms + [PRICE_LIST_UPLOAD_PERMISSION]
        return super().login(**kwargs)


class TutorialTests(TestCase):
    def test_get_is_ok(self):
        res = self.client.get('/data-capture/tutorial')
        self.assertEqual(res.status_code, 200)


class Step1Tests(PriceListStepTestCase):
    url = '/data-capture/step/1'

    valid_form = {
        'schedule': FAKE_SCHEDULE,
        'contract_number': 'GS-123-4567'
    }

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_valid_post_sets_session_data(self):
        self.login()
        self.client.post(self.url, self.valid_form)
        session_pl = self.client.session['data_capture:price_list']
        session_data = session_pl['step_1_POST']
        self.assertEqual(session_data['schedule'], FAKE_SCHEDULE)
        self.assertEqual(session_data['contract_number'], 'GS-123-4567')

    def test_valid_post_does_not_overwrite_other_step_data_if_exists(self):
        self.login()
        # save step 2 data into session before POSTing step 1 data
        session = self.client.session
        session['data_capture:price_list'] = {
            'step_2_POST': Step2Tests.valid_form,
        }
        session.save()
        self.client.post(self.url, self.valid_form)
        # need to grab session again after POST
        session = self.client.session
        self.assertEqual(session['data_capture:price_list']['step_2_POST'],
                         Step2Tests.valid_form)

    @override_settings(
        DATA_CAPTURE_SCHEDULES=[
            FAKE_SCHEDULE,
            'data_capture.schedules.s70.Schedule70PriceList'],
    )
    def test_valid_post_with_diff_schedule_removes_gleaned_data(self):
        self.login()

        # first, post with Fake Schedule selected
        self.client.post(self.url, self.valid_form)
        # Save gleaned data into session
        self.set_fake_gleaned_data(rows=Step3Tests.rows)
        session = self.client.session
        self.assertIn('gleaned_data', session['data_capture:price_list'])
        # Post again but with a different schedule selected
        self.client.post(self.url, {
            'schedule': 'data_capture.schedules.s70.Schedule70PriceList',
            'contract_number': 'GS-123-4567', })
        session = self.client.session
        # gleaned_data should now be removed from session
        self.assertNotIn('gleaned_data', session['data_capture:price_list'])

        # Save Fake gleaned data again now the S70 has been "selected"
        self.set_fake_gleaned_data(rows=Step3Tests.rows)
        session = self.client.session
        self.assertIn('gleaned_data', session['data_capture:price_list'])
        # Post valid again, but selecting Fake Schedule
        self.client.post(self.url, self.valid_form)
        session = self.client.session
        # gleaned_data should still be in session
        self.assertIn('gleaned_data', session['data_capture:price_list'])

    def test_valid_post_redirects_to_step_2(self):
        self.login()
        res = self.client.post(self.url, self.valid_form)
        self.assertRedirects(res, Step2Tests.url)

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops! Please correct the following errors.'
        )

    def test_duplicate_contract_post_returns_html(self):
        mommy.make(SubmittedPriceList,
                   contract_number='gs-boop')
        self.login()
        res = self.client.post(self.url, {
            'schedule': FAKE_SCHEDULE,
            'contract_number': 'gs-boop'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'A price list with this contract number has '
                                 'already been submitted.')
        self.assertContains(res, 'We found an <a href=')
        self.assertContains(
            res,
            'existing price list</a> for contract number gs-boop.'
        )

    def test_duplicate_contract_post_message_contract_num_is_escaped(self):
        mommy.make(SubmittedPriceList,
                   contract_number='<boop>')
        self.login()
        res = self.client.post(self.url, {
            'schedule': FAKE_SCHEDULE,
            'contract_number': '<boop>'})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'We found an <a href=')
        self.assertContains(
            res,
            'existing price list</a> for contract number &lt;boop&gt;.'
        )


class Step2Tests(PriceListStepTestCase, HandleCancelMixin):
    url = '/data-capture/step/2'

    valid_form = {
        'vendor_name': 'foo',
        'contractor_site': 'Customer',
        'is_small_business': 'False',
        'contract_start_0': '1985',
        'contract_start_1': '07',
        'contract_start_2': '08',
        'contract_end_0': '1989',
        'contract_end_1': '04',
        'contract_end_2': '14'
    }

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = {
            'step_1_POST': Step1Tests.valid_form,
        }
        session.save()

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_going_back_to_previous_step_prefills_its_form(self):
        self.login()
        res = self.client.get(Step1Tests.url)
        self.assertEqual(res.context['form'].data, Step1Tests.valid_form)

    def test_redirects_to_step_1_if_not_completed(self):
        self.login()
        self.delete_price_list_from_session()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step1Tests.url)

    def test_valid_post_updates_session_data(self):
        self.login()
        self.client.post(self.url, self.valid_form)
        session_pl = self.client.session['data_capture:price_list']
        posted_data = session_pl['step_2_POST']
        self.assertEqual(posted_data['contractor_site'],
                         self.valid_form['contractor_site'])
        self.assertEqual(posted_data['is_small_business'],
                         self.valid_form['is_small_business'])
        self.assertEqual(posted_data['vendor_name'],
                         self.valid_form['vendor_name'])

    def test_valid_post_redirects_to_step_3(self):
        self.login()
        res = self.client.post(self.url, self.valid_form)
        self.assertRedirects(res, Step3Tests.url)

    def test_invalid_post_returns_html(self):
        self.login()
        res = self.client.post(self.url, {})
        self.assertEqual(res.status_code, 200)
        self.assertContains(res, 'This field is required')
        self.assertHasMessage(
            res,
            'error',
            'Oops! Please correct the following errors.'
        )


class Step3Tests(PriceListStepTestCase, HandleCancelMixin):
    url = '/data-capture/step/3'

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    invalid_rows = [rows[0].copy()]
    invalid_rows[0]['education'] = 'Bachelorz'

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = {
            'step_1_POST': Step1Tests.valid_form,
            'step_2_POST': Step2Tests.valid_form,
        }
        session.save()

    def ajax_post(self, data):
        res = self.client.post(self.url, data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        return res, json.loads(res.content.decode('utf-8'))

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def test_going_back_to_previous_step_prefills_its_form(self):
        self.login()
        res = self.client.get(Step2Tests.url)
        self.assertEqual(res.context['form'].data, Step2Tests.valid_form)

    def test_redirects_to_step_2_if_not_completed(self):
        self.login()
        self.delete_price_list_from_session()
        res = self.client.get(self.url)
        self.assertRedirects(res, Step2Tests.url, target_status_code=302)

    def test_replay_works(self):
        user = self.login(is_staff=True,
                          permissions=[VIEW_ATTEMPT_PERMISSION])
        attempt = AttemptedPriceListSubmission(
            submitter=user,
            session_state=self.client.session['data_capture:price_list'],
        )
        attempt.set_uploaded_file(uploaded_csv_file())
        attempt.save()
        self.delete_price_list_from_session()
        res = self.client.post(self.url, {
            'replay-attempted-submission': str(attempt.id)
        })
        self.assertRedirects(res, Step4Tests.url)

        # Ensure that an additional replay wasn't created as a result
        # of the replay.
        self.assertEqual(AttemptedPriceListSubmission.objects.all().count(),
                         1)

    def test_replay_is_forbidden_for_non_tech_support_folks(self):
        self.login(is_staff=True)
        res = self.client.post(self.url, {
            'replay-attempted-submission': '1'
        })
        self.assertEqual(res.status_code, 403)

    def assertExistingFilename(self, res, value):
        self.assertEqual(
            res.context['form'].fields['file'].widget.existing_filename,
            value
        )

    def test_not_prefilled_if_no_gleaned_data_in_session(self):
        self.login()
        self.assertExistingFilename(self.client.get(self.url), None)

    def test_not_prefilled_if_gleaned_data_has_no_valid_rows(self):
        self.login()
        self.set_fake_gleaned_data(self.invalid_rows)
        self.assertExistingFilename(self.client.get(self.url), None)

    def test_prefilled_if_gleaned_data_in_session_with_valid_rows(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        self.assertExistingFilename(self.client.get(self.url), 'foo.csv')

    def test_empty_prefilled_post_with_no_invalid_rows_works(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.post(self.url, {})
        self.assertRedirects(res, Step4Tests.url)

    def test_empty_prefilled_post_with_some_invalid_rows_works(self):
        self.login()
        self.set_fake_gleaned_data(self.rows + self.invalid_rows)
        res = self.client.post(self.url, {})
        self.assertRedirects(res, Step3ErrorTests.url)

    def test_valid_post_updates_session_data(self):
        self.login()
        self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        session_pl = self.client.session['data_capture:price_list']
        self.assertEqual(session_pl['step_1_POST']['schedule'],
                         FAKE_SCHEDULE)
        gleaned_data = session_pl['gleaned_data']
        gleaned_data = registry.deserialize(gleaned_data)
        assert isinstance(gleaned_data, FakeSchedulePriceList)
        self.assertEqual(gleaned_data.rows, [{
            'education': 'Bachelors',
            'price': '15.00',
            'service': 'Project Manager',
            'sin': '132-40',
            'years_experience': '7'
        }])
        self.assertEqual(session_pl['filename'], 'foo.csv')

    def test_post_with_gleaned_data_and_uploaded_file_checks_validity(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.post(self.url, {
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertRedirects(res, Step3ErrorTests.url)

    def test_valid_post_via_xhr_returns_json(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file()
        })
        self.assertEqual(json_data, {
            'redirect_url': Step4Tests.url
        })

    def test_post_with_invalid_rows_via_xhr_returns_json_redirect(self):
        self.login()
        res, json_data = self.ajax_post({
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertEqual(json_data, {
            'redirect_url': Step3ErrorTests.url
        })

    def test_valid_post_redirects_to_step_4(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file()
        })
        self.assertRedirects(res, Step4Tests.url)

    def test_post_with_invalid_rows_redirects_to_step_3_errors(self):
        self.login()
        res = self.client.post(self.url, {
            'file': uploaded_csv_file(
                content=create_csv_content(rows=[
                    ['132-40', 'Project Manager', 'invalid edu', '7', '15.00']
                ]))
        })
        self.assertRedirects(res, Step3ErrorTests.url)

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

    def test_invalid_post_via_xhr_returns_json(self):
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


class Step3ErrorTests(PriceListStepTestCase,
                      RequireGleanedDataMixin,
                      HandleCancelMixin):
    url = '/data-capture/step/3/errors'

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }]

    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    def setUp(self):
        super().setUp()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()

    def test_get_is_ok(self):
        self.login()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)


class Step4Tests(PriceListStepTestCase,
                 HandleCancelMixin, RequireGleanedDataMixin):
    url = '/data-capture/step/4'

    rows = [{
        'education': 'Bachelors',
        'price': '15.00',
        'service': 'Project Manager',
        'sin': '132-40',
        'years_experience': '7'
    }, {
        'education': 'School of hard knocks',
        'price': '0',
        'service': 'Oil change & tune up',
        'sin': 'absolved',
        'years_experience': 'vii'
    }]
    session_data = {
        'step_1_POST': Step1Tests.valid_form,
        'step_2_POST': Step2Tests.valid_form,
    }

    valid_post_data = {}
    valid_post_data.update(Step1Tests.valid_form)
    valid_post_data.update(Step2Tests.valid_form)

    def test_get_is_ok(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url)
        self.assertFalse(res.context['show_edit_form'])
        self.assertEqual(res.status_code, 200)

    def test_context_has_prev_url_if_query_param_present(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url + '?prev={}'.format(Step2Tests.url))
        self.assertEqual(res.status_code, 200)
        self.assertIn('prev_url', res.context)
        self.assertEqual(res.context['prev_url'], '/data-capture/step/2')

    def test_prev_url_is_none_if_query_param_not_safe(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.get(self.url + '?prev={}'.format('http://foo.com'))
        self.assertEqual(res.status_code, 200)
        self.assertIn('prev_url', res.context)
        self.assertEqual(res.context['prev_url'], None)

    def test_redirects_if_no_gleaned_data(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], Step3Tests.url)

    def test_redirects_if_no_valid_rows_in_gleaned_data(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data([])
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], Step3Tests.url)

    def test_gleaned_data_with_valid_rows_is_required_on_POST(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data([])
        res = self.client.post(self.url)
        self.assertEqual(res.status_code, 400)

    def test_saving_changes_saves_and_redirects_back_to_self(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        data = self.valid_post_data.copy()
        data['vendor_name'] = 'changed in step 4!'
        data['contractor_site'] = 'Both'
        data['save-changes'] = ''
        res = self.client.post(self.url, data)
        session_pl = self.client.session['data_capture:price_list']
        step_1_data = session_pl['step_1_POST']
        self.assertEqual(step_1_data['schedule'], FAKE_SCHEDULE)
        self.assertEqual(step_1_data['contract_number'], 'GS-123-4567')
        self.assertEqual(step_1_data['vendor_name'], 'changed in step 4!')
        step_2_data = session_pl['step_2_POST']
        self.assertEqual(step_2_data['contractor_site'], 'Both')
        self.assertEqual(SubmittedPriceList.objects.all().count(), 0)
        self.assertRedirects(res, Step4Tests.url)

    def test_invalid_post_shows_errors(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        data = self.valid_post_data.copy()
        data['contractor_site'] = 'LOL'
        res = self.client.post(self.url, data)
        self.assertTrue(res.context['show_edit_form'])
        self.assertContains(res, 'LOL is not one of the available choices')

    @freeze_time(frozen_datetime)
    def test_valid_post_creates_models(self):
        user = self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        self.client.post(self.url, self.valid_post_data)
        p = SubmittedPriceList.objects.filter(
            contract_number='GS-123-4567'
        )[0]
        self.assertEqual(p.schedule, FAKE_SCHEDULE)
        self.assertEqual(p.vendor_name, 'foo')
        self.assertEqual(p.contractor_site, 'Customer')
        self.assertEqual(p.is_small_business, False)
        self.assertEqual(p.submitter, user)
        self.assertEqual(p.status_changed_by, user)
        self.assertEqual(p.status, SubmittedPriceList.STATUS_UNREVIEWED)
        self.assertEqual(p.status_changed_at,
                         timezone.make_aware(frozen_datetime))
        self.assertEqual(p.uploaded_filename, 'foo.csv')

    def test_valid_post_clears_session_and_redirects_to_step_5(self):
        self.login()
        session = self.client.session
        session['data_capture:price_list'] = self.session_data
        session.save()
        self.set_fake_gleaned_data(self.rows)
        res = self.client.post(self.url, self.valid_post_data)
        assert 'data_capture:price_list' not in self.client.session
        self.assertRedirects(res, Step5Tests.url)


class Step5Tests(PriceListStepTestCase):
    url = '/data-capture/step/5'

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
