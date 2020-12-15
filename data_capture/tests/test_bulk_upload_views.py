import json
import unittest

from django.core.files.base import ContentFile

from ..management.commands.initgroups import BULK_UPLOAD_PERMISSION
# from .test_jobs import process_worker_jobs
from .common import (StepTestCase, R10_XLSX_PATH, XLSX_CONTENT_TYPE,
                     create_bulk_upload_contract_source)
from ..views import bulk_upload

from contracts.models import BulkUploadContractSource


class BulkUploadViewTests(unittest.TestCase):
    def test_render_upload_example_works(self):
        html = bulk_upload.render_r10_spreadsheet_example()
        self.assertTrue('Labor Category' in html)
        self.assertTrue('Contract Year' in html)


class R10StepTestCase(StepTestCase):
    url = None

    def setUp(self):
        super().setUp()
        session = self.client.session
        session.clear()

    def login(self, **kwargs):
        kwargs['permissions'] = [BULK_UPLOAD_PERMISSION]
        return super().login(**kwargs)

    def setup_upload_source(self, user):
        src = create_bulk_upload_contract_source(user)
        src.save()
        session = self.client.session
        session['data_capture:upload_source_id'] = src.pk
        session.save()
        return src


class Region10UploadStep1Tests(R10StepTestCase):
    url = '/data-capture/bulk/region-10/step/1'

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)

    def ajax_post(self, data):
        res = self.client.post(self.url, data,
                               HTTP_X_REQUESTED_WITH='XMLHttpRequest')
        self.assertEqual(res.status_code, 200)
        return res, json.loads(res.content.decode('utf-8'))

    def test_valid_post_creates_upload_source_sets_session_data(self):
        user = self.login()
        with open(R10_XLSX_PATH, 'rb') as f:
            self.client.post(self.url, {'file': f})
            upload_source = BulkUploadContractSource.objects.all()[0]
            self.assertEqual(upload_source.procurement_center,
                             BulkUploadContractSource.REGION_10)
            self.assertEqual(upload_source.file_mime_type, XLSX_CONTENT_TYPE)
            f.seek(0)  # reseek back to start so it can be read again
            self.assertEqual(ContentFile(upload_source.original_file).read(),
                             f.read())
            self.assertEqual(
                self.client.session['data_capture:upload_source_id'],
                upload_source.pk)
            self.assertEqual(user, upload_source.submitter)
            self.assertFalse(upload_source.has_been_loaded)

    def test_valid_post_redirects_to_step_2(self):
        self.login()
        with open(R10_XLSX_PATH, 'rb') as f:
            res = self.client.post(self.url, {'file': f})
            self.assertRedirects(res, Region10UploadStep2Tests.url)

    def test_valid_ajax_post_returns_json(self):
        self.login()
        with open(R10_XLSX_PATH, 'rb') as f:
            res, json_data = self.ajax_post({
                'file': f
            })
            self.assertEqual(json_data, {
                'redirect_url': Region10UploadStep2Tests.url
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


class Region10UploadStep2Tests(R10StepTestCase):
    url = '/data-capture/bulk/region-10/step/2'

    def test_session_source_id_is_required(self):
        self.login()
        res = self.client.get(self.url)
        self.assertRedirects(res, Region10UploadStep1Tests.url)

    def test_get_is_ok(self):
        user = self.login()
        self.setup_upload_source(user)
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('file_metadata', res.context)

    # def test_post_is_ok_and_contracts_are_created_properly(self):
    #     user = self.login()
    #     self.setup_upload_source(user)
    #     res = self.client.post(self.url)
    #     self.assertRedirects(res, Region10UploadStep3Tests.url)

    #     process_worker_jobs()

    #     contracts = Contract.objects.all()
    #     self.assertEqual(len(contracts), 3)
    #     upload_source = BulkUploadContractSource.objects.all()[0]
    #     self.assertTrue(upload_source.has_been_loaded)
    #     for c in contracts:
    #         self.assertIsNotNone(c.search_index)
    #     self.assertNotIn('data_capture:upload_source_id', self.client.session)

    # def test_old_contracts_are_deleted(self):
    #     user = self.login()
    #     other_source = BulkUploadContractSource.objects.create(
    #         procurement_center=BulkUploadContractSource.REGION_10
    #     )
    #     Contract.objects.create(
    #         min_years_experience=1,
    #         hourly_rate_year1=20.20,
    #         idv_piid='abc',
    #         vendor_name='blah',
    #         labor_category='whatever',
    #         upload_source=other_source
    #     )
    #     self.setup_upload_source(user)
    #     res = self.client.post(self.url)
    #     self.assertRedirects(res, Region10UploadStep3Tests.url)

    #     process_worker_jobs()

    #     contracts = Contract.objects.all()
    #     self.assertEqual(len(contracts), 3)

    def test_cancel_clears_session_and_redirects(self):
        user = self.login()
        self.setup_upload_source(user)
        res = self.client.post(self.url, {'cancel': ''})
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['Location'], '/')
        session = self.client.session
        self.assertNotIn('data_capture:upload_source_id', session)


class Region10UploadStep3Tests(R10StepTestCase):
    url = '/data-capture/bulk/region-10/step/3'

    def test_get_is_ok(self):
        self.login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 200)
        self.assertIn('SEND_TRANSACTIONAL_EMAILS', res.context)
