from model_mommy import mommy
from django.test import TestCase, override_settings

from .common import FAKE_SCHEDULE, uploaded_csv_file, r10_file
from ..schedules.fake_schedule import FakeSchedulePriceList
from ..forms import (Step1Form, Step2Form, PriceListUploadForm, Step4Form,
                     PriceListDetailsForm, Region10BulkUploadForm)
from ..models import SubmittedPriceList


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class Step1FormTests(TestCase):
    def make_form(self, contract_number='GS-BOOP'):
        return Step1Form({
            'contract_number': contract_number,
            'schedule': FAKE_SCHEDULE,
        })

    def test_clean_contract_number_works(self):
        mommy.make(SubmittedPriceList,
                   contract_number='GS-BOOP')
        form = self.make_form()
        self.assertFalse(form.is_valid())
        self.assertIn('contract_number', form.errors)
        self.assertIn('A price list with this contract number has already '
                      'been submitted.',
                      form.errors['contract_number'])

        form = self.make_form(contract_number='GS-NOT-DUPE')
        self.assertTrue(form.is_valid())

    def test_clean_contract_number_is_case_insensitive(self):
        mommy.make(SubmittedPriceList,
                   contract_number='GS-BOOP')
        form = self.make_form(contract_number='gs-boop')
        self.assertFalse(form.is_valid())
        self.assertIn('contract_number', form.errors)
        self.assertIn('A price list with this contract number has already '
                      'been submitted.',
                      form.errors['contract_number'])

    def test_contract_number_format_is_validated(self):
        form = self.make_form(contract_number='***GS-123-BOOP')
        self.assertFalse(form.is_valid())
        self.assertIn('contract_number', form.errors)
        self.assertIn('Please use only letters, numbers, and dashes (-).',
                      form.errors['contract_number'])

    def test_has_existing_contract_number_error_works(self):
        mommy.make(SubmittedPriceList,
                   contract_number='GS-BOOP')
        form = self.make_form()
        form.is_valid()
        self.assertTrue(form.has_existing_contract_number_error())

        form = self.make_form('GS-NOT-DUPE')
        form.is_valid()
        self.assertFalse(form.has_existing_contract_number_error())


class Step2FormTests(TestCase):
    form_class = Step2Form

    def test_clean_escalation_rate_works(self):
        form = self.form_class({'escalation_rate': None})
        form.is_valid()
        self.assertEqual(form.cleaned_data['escalation_rate'], 0)

        form = self.form_class({'escalation_rate': 2.5})
        form.is_valid()
        self.assertEqual(form.cleaned_data['escalation_rate'], 2.5)

    def test_contract_start_and_end_date_is_validated(self):
        form = self.form_class({
            'contract_start_0': '2020',
            'contract_start_1': '01',
            'contract_start_2': '1',
            'contract_end_0': '2015',
            'contract_end_1': '01',
            'contract_end_2': '01',
            'contractor_site': 'Both',
            'is_small_business': True,
        })
        self.assertFalse(form.is_valid())
        self.assertIn('contract_start', form.errors)
        self.assertEqual(form.errors['contract_start'][0],
                         'Start date must be before end date.')


@override_settings(DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE])
class PriceListUploadFormTests(TestCase):
    def test_invalid_when_file_is_missing(self):
        form = PriceListUploadForm({}, schedule=FAKE_SCHEDULE)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'][0], 'This field is required.')

    def test_valid_when_file_is_missing_and_not_required(self):
        form = PriceListUploadForm(
            {}, schedule=FAKE_SCHEDULE, is_file_required=False)
        self.assertTrue(form.is_valid())

    def test_invalid_when_file_cannot_be_gleaned(self):
        form = PriceListUploadForm({}, {
            'file': uploaded_csv_file(b'i cannot be gleaned')
        }, schedule=FAKE_SCHEDULE)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [
                "The file you uploaded doesn't have any data we can "
                "glean from it."
            ]
        })

    def test_clean_sets_gleaned_data(self):
        form = PriceListUploadForm({}, {
            'file': uploaded_csv_file()
        }, schedule=FAKE_SCHEDULE)
        self.assertTrue(form.is_valid())
        self.assertEqual(form.cleaned_data['gleaned_data'].title,
                         FakeSchedulePriceList.title)


class Step4FormTests(Step2FormTests):
    form_class = Step4Form

    def test_meta_fields_are_combination_of_steps_1_and_2(self):
        self.assertEqual(
            Step1Form.Meta.fields + Step2Form.Meta.fields,
            Step4Form.Meta.fields
        )

    def test_from_post_data_subsets_works(self):
        form = Step4Form.from_post_data_subsets({'a': 1}, {'b': 2})
        self.assertEqual(form.data, {
            'a': 1,
            'b': 2
        })


class PriceListDetailsFormTests(TestCase):
    def test_is_different_from_works(self):
        price_list = mommy.make(SubmittedPriceList,
                                vendor_name='Seppi Socks Co.')
        form = PriceListDetailsForm(instance=price_list)
        self.assertFalse(form.is_different_from(price_list))

        new_price_list = SubmittedPriceList(price_list)
        new_price_list.vendor_name = 'Vendy Vend, Inc'
        self.assertTrue(form.is_different_from(new_price_list))


class Region10BulkUploadFormTests(TestCase):
    def test_invalid_when_file_is_missing(self):
        form = Region10BulkUploadForm({})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['file'][0], 'This field is required.')

    def test_invalid_when_file_is_invalid(self):
        form = Region10BulkUploadForm({}, {'file': r10_file(b'whatever')})
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors, {
            '__all__': [
                "That file does not appear to be a "
                "valid Region 10 export. Try another?"
            ]
        })

    def test_valid_when_file_is_valid(self):
        form = Region10BulkUploadForm({}, {'file': r10_file()})
        self.assertTrue(form.is_valid())
