from typing import Dict, Any
from django import forms
from django.core.exceptions import ValidationError
from uswds_forms import UswdsRadioSelect, UswdsDateField

from ..models import SubmittedPriceList
from ..schedules import registry
from frontend.upload import UploadWidget
from contracts.models import MIN_ESCALATION_RATE, MAX_ESCALATION_RATE


class DuplicateContractValidationError(ValidationError):
    pass


def ensure_contract_start_is_before_end(form, cleaned_data):
    start = cleaned_data.get('contract_start')
    end = cleaned_data.get('contract_end')
    if start and end and start > end:
        form.add_error('contract_start',
                       'Start date must be before end date.')


class EscalationRateField(forms.FloatField):
    def __init__(self):
        super().__init__(
            label="Escalation rate (%)",
            help_text='CALC uses the escalation rate (as a percentage) '
                      'to calculate out-year pricing. '
                      'Leave this field blank or enter 0 if this contract '
                      'does not have a fixed escalation rate.',
            min_value=MIN_ESCALATION_RATE,
            max_value=MAX_ESCALATION_RATE,
            required=False
        )

    def clean(self, value):
        value = super().clean(value)
        if value is None:
            value = 0
        return value


class Step1Form(forms.ModelForm):
    schedule = forms.ChoiceField(
        label="Which schedule is associated with this price list?",
        choices=registry.get_choices
    )

    class Meta:
        model = SubmittedPriceList
        fields = [
            'schedule',
            'contract_number',
        ]

    def has_existing_contract_number_error(self):
        if 'contract_number' in self.errors:
            for err in self.errors.as_data()['contract_number']:
                if isinstance(err, DuplicateContractValidationError):
                    return True
        return False

    def clean(self):
        cleaned_data = super().clean()
        schedule = cleaned_data.get('schedule')
        if schedule:
            cleaned_data['schedule_class'] = registry.get_class(schedule)
        return cleaned_data

    def clean_contract_number(self):
        '''
        Raises a DuplicateContractValidationError if a SubmittedPriceList
        with the same contract number (case-insensitive) already exists.
        '''
        value = self.cleaned_data['contract_number']

        is_duplicate = SubmittedPriceList.objects.filter(
            contract_number__iexact=value).exists()
        if is_duplicate:
            raise DuplicateContractValidationError(
                'A price list with this contract number has '
                'already been submitted.')

        return value


class Step2Form(forms.ModelForm):
    is_small_business = forms.ChoiceField(
        label='Business size',
        choices=[
            (True, 'This is a small business.'),
            (False, 'This is not a small business.'),
        ],
        widget=UswdsRadioSelect,
    )
    contractor_site = forms.ChoiceField(
        label='Worksite',
        choices=SubmittedPriceList.CONTRACTOR_SITE_CHOICES,
        widget=UswdsRadioSelect,
    )
    contract_start = UswdsDateField(
        label='Contract or current option period start'
    )
    contract_end = UswdsDateField(
        label='Contract or current option period end'
    )
    escalation_rate = EscalationRateField()

    def clean(self):
        cleaned_data = super().clean()
        ensure_contract_start_is_before_end(self, cleaned_data)
        return cleaned_data

    class Meta:
        model = SubmittedPriceList
        fields = [
            'vendor_name',
            'is_small_business',
            'contractor_site',
            'contract_start',
            'contract_end',
            'escalation_rate'
        ]


class PriceListUploadForm(forms.Form):
    file = forms.FileField(widget=UploadWidget())

    def __init__(self, *args, **kwargs):
        '''
        This constructor requires `schedule` to be passed in as a
        keyword argument. It should be a string referring to the
        fully-qualified class name for an entry in the schedule
        registry, e.g.
        "data_capture.schedules.fake_schedule.FakeSchedulePriceList".

        `is_file_required` may also be passed in as a keyword argument to
        indicate whether the file field of this form is required. It
        defaults to True. If it is False, then the file field of this form
        will not be required.

        `existing_filename` may also be passed as a keyword argument
        to indicate the name of an existing file that was uploaded earlier.
        It defaults to None.
        '''

        self.schedule = kwargs.pop('schedule')
        self.schedule_class = registry.get_class(self.schedule)

        is_file_required = kwargs.pop('is_file_required', True)
        existing_filename = kwargs.pop('existing_filename', None)

        super().__init__(*args, **kwargs)

        extra = self.schedule_class.upload_widget_extra_instructions
        if extra is not None:
            self.fields['file'].widget.extra_instructions = extra

        self.fields['file'].required = is_file_required
        self.fields['file'].widget.required = is_file_required
        self.fields['file'].widget.existing_filename = existing_filename

    def clean(self):
        cleaned_data = super().clean()
        file = cleaned_data.get('file')

        if file:
            gleaned_data = registry.smart_load_from_upload(self.schedule,
                                                           file)

            if gleaned_data.is_empty():
                raise forms.ValidationError(
                    "The file you uploaded doesn't have any data we can "
                    "glean from it."
                )

            cleaned_data['gleaned_data'] = gleaned_data

        return cleaned_data


class PriceListDetailsForm(forms.ModelForm):
    is_small_business = forms.ChoiceField(
        label='Business size',
        choices=[
            (True, 'This is a small business.'),
            (False, 'This is not a small business.'),
        ],
        widget=UswdsRadioSelect,
    )
    contractor_site = forms.ChoiceField(
        label='Worksite',
        choices=SubmittedPriceList.CONTRACTOR_SITE_CHOICES,
        widget=UswdsRadioSelect,
    )
    contract_start = UswdsDateField(
        label='Contract or current option period start'
    )
    contract_end = UswdsDateField(
        label='Contract or current option period end'
    )
    escalation_rate = EscalationRateField()

    def clean(self):
        cleaned_data = super().clean()
        ensure_contract_start_is_before_end(self, cleaned_data)
        return cleaned_data

    def is_different_from(self, price_list):
        my_model = self.save(commit=False)
        for field in self.Meta.fields:
            if getattr(my_model, field) != getattr(price_list, field):
                return True
        return False

    class Meta:
        model = SubmittedPriceList
        fields = ['vendor_name', 'is_small_business', 'contractor_site',
                  'contract_start', 'contract_end', 'escalation_rate']


class Step4Form(PriceListDetailsForm):
    schedule = forms.ChoiceField(
        choices=registry.get_choices,
        widget=forms.HiddenInput()
    )

    class Meta:
        model = SubmittedPriceList
        fields = Step1Form.Meta.fields + Step2Form.Meta.fields

    @classmethod
    def from_post_data_subsets(cls, *post_datas):
        '''
        This form is basically a superset of the data from earlier steps,
        and this method makes it easy to pass in the POST data from those
        earlier steps to obtain an instance of this form.
        '''

        combined_post_data: Dict[str, Any] = {}
        for post_data in post_datas:
            combined_post_data.update(post_data)
        return cls(combined_post_data)
