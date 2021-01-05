import csv
import logging
from io import StringIO

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from contracts.models import EDUCATION_CHOICES as _EDUCATION_CHOICES
from .base import BasePriceList, min_price_validator


EDU_LEVELS = {}

for _code, _name in _EDUCATION_CHOICES:
    EDU_LEVELS[_name] = _code

del _code
del _name

logger = logging.getLogger('calc')


def validate_education_level(value):
    values = EDU_LEVELS.keys()
    if value not in values:
        raise ValidationError('This field must contain one of the '
                              'following values: %s' % (', '.join(values)))


class FakeScheduleRow(forms.Form):
    sin = forms.CharField(label="SIN")
    service = forms.CharField(label="Service proposed")
    education = forms.CharField(
        label="Minimum education",
        validators=[validate_education_level]
    )
    years_experience = forms.IntegerField(
        label="Minimum years of experience"
    )
    price = forms.DecimalField(
        label="Price",
        validators=[min_price_validator])


class FakeSchedulePriceList(BasePriceList):
    title = 'Fake Schedule (for dev/debugging only)'
    table_template = 'data_capture/price_list/tables/fake_schedule.html'
    upload_example_template = ('data_capture/price_list/upload_examples/'
                               'fake_schedule.html')
    upload_widget_extra_instructions = 'CSV format, please.'

    def __init__(self, rows):
        super().__init__()

        self.rows = rows

        for row in self.rows:
            form = FakeScheduleRow(row)
            if form.is_valid():
                self.valid_rows.append(form)
            else:
                self.invalid_rows.append(form)

    def add_to_price_list(self, price_list):
        for row in self.valid_rows:
            price_list.add_row(
                labor_category=row['service'].value(),
                education_level=EDU_LEVELS[row['education'].value()],
                min_years_experience=row['years_experience'].value(),
                base_year_rate=row['price'].value(),
                sin=row['sin'].value()
            )

    def serialize(self):
        return self.rows

    def to_table(self):
        return render_to_string(self.table_template,
                                {'rows': self.valid_rows})

    def to_error_table(self):
        return render_to_string(self.table_template,
                                {'rows': self.invalid_rows})

    @classmethod
    def deserialize(cls, rows):
        return cls(rows)

    @classmethod
    def load_from_upload(cls, f):
        try:
            reader = csv.DictReader(StringIO(f.read().decode('utf-8')))
            return cls([row for row in reader])
        except Exception as e:
            logger.info('Failed to glean data from %s: %s' % (f.name, e))
            raise ValidationError(
                'Weird problems occurred when reading your file.'
            )
