import xlrd
import functools

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .base import (BasePriceList, hourly_rates_only_validator,
                   min_price_validator)
from .spreadsheet_utils import generate_column_index_map, safe_cell_str_value
from .coercers import (strip_non_numeric, extract_min_education,
                       extract_hour_unit_of_issue)
from contracts.models import EDUCATION_CHOICES

DEFAULT_SHEET_NAME = 'Labor Category'

EXAMPLE_SHEET_ROWS = [
    [
        r'SIN(s) PROPOSED',
        r'SERVICE PROPOSED (e.g. Job Title/Task)',
        r'MINIMUM EDUCATION/ CERTIFICATION LEVEL',
        r'MINIMUM YEARS OF EXPERIENCE',
        r'COMMERCIAL LIST PRICE (CPL)   OR MARKET  PRICES',
        r'UNIT OF ISSUE (e.g. Hour, Task, Sq ft)',
        r'MOST FAVORED CUSTOMER (MFC)',
        r'DISCOUNT OFFERED TO MFC (%)',
        r'MFC PRICE',
        r'GSA(%) DISCOUNT (exclusive of the .75% IFF)',
        r'PRICE OFFERED TO GSA (excluding IFF)',
        r'PRICE OFFERED TO GSA (including IFF)',
        r'QUANTITY/VOLUME DISCOUNT',
    ],
    [
        r'712-3',
        r'Project Manager',
        r'High School',
        r'3',
        r'',
        r'',
        r'',
        r'',
        r'',
        r'',
        r'',
        r'95.00',
        r'',
    ],
]


DEFAULT_FIELD_TITLE_MAP = {
    'sin': 'SIN(s) Proposed',
    'labor_category': 'Service Proposed (e.g. Job Title/Task)',  # noqa
    'education_level': 'Minimum Education / Certification Level',
    'min_years_experience': 'Minimum Years of Experience',
    'unit_of_issue': 'Unit of Issue (e.g. Hour, Task, Sq Ft)',
    'price_including_iff': 'Price Offered to GSA (including IFF)',
}


def glean_labor_categories_from_file(f, sheet_name=DEFAULT_SHEET_NAME):
    book = xlrd.open_workbook(file_contents=f.read())
    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):

    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    rownum = 1  # start on first row after heading row

    cats = []

    heading_row = sheet.row(0)

    col_idx_map = generate_column_index_map(heading_row,
                                            DEFAULT_FIELD_TITLE_MAP)

    coercion_map = {
        'price_including_iff': strip_non_numeric,
        'min_years_experience': int,
        'education_level': extract_min_education,
        'unit_of_issue': extract_hour_unit_of_issue,
    }

    while True:
        cval = functools.partial(safe_cell_str_value, sheet, rownum)

        sin = cval(col_idx_map['sin'])
        price_including_iff = cval(col_idx_map['price_including_iff'],
                                   coercer=strip_non_numeric)

        is_price_ok = (price_including_iff.strip() and
                       float(price_including_iff) > 0)

        if not sin.strip() and not is_price_ok:
            break

        cat = {}

        for field, col_idx in col_idx_map.items():
            coercer = coercion_map.get(field, None)
            cat[field] = cval(col_idx, coercer=coercer)

        cats.append(cat)

        rownum += 1

    return cats


class Region3PriceListRow(forms.Form):
    sin = forms.CharField(label='SIN(s) Proposed')
    labor_category = forms.CharField(
        label="SERVICE PROPOSED (e.g. Job Title/Task)"
    )
    education_level = forms.CharField(
        label="Minimum Education / Certification Level"
    )
    min_years_experience = forms.IntegerField(
        label="Minimum Years of Experience"
    )
    unit_of_issue = forms.CharField(
        label="Unit of issue",
        required=True,
        validators=[hourly_rates_only_validator]
    )
    price_including_iff = forms.DecimalField(
        label='Price Offered to GSA (including IFF)',
        validators=[min_price_validator]
    )

    def clean_education_level(self):
        value = self.cleaned_data['education_level']

        values = [choice[1] for choice in EDUCATION_CHOICES]

        if value not in values:
            raise ValidationError('This field must contain one of the '
                                  'following values: %s' % (', '.join(values)))

        return value

    def contract_model_education_level(self):
        # Note that due to the way we've cleaned education_level, this
        # code is guaranteed to work.
        return [
            code for code, name in EDUCATION_CHOICES
            if name == self.cleaned_data['education_level']
        ][0]

    def contract_model_base_year_rate(self):
        return self.cleaned_data['price_including_iff']


class Region3PriceList(BasePriceList):

    title = '71_IIK'

    table_template = 'data_capture/price_list/tables/region_3.html'

    upload_example_template = ('data_capture/price_list/upload_examples/'
                               'region_3.html')

    upload_widget_extra_instructions = 'XLS or XLSX format, please.'

    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        for row in self.rows:
            form = Region3PriceListRow(row)
            if form.is_valid():
                self.valid_rows.append(form)
            else:
                self.invalid_rows.append(form)

    def add_to_price_list(self, price_list):
        for row in self.valid_rows:
            price_list.add_row(
                labor_category=row.cleaned_data['labor_category'],
                education_level=row.contract_model_education_level(),
                min_years_experience=row.cleaned_data['min_years_experience'],
                base_year_rate=row.contract_model_base_year_rate(),
                sin=row.cleaned_data['sin']
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
    def get_upload_example_context(cls):
        return {
            'sheet_name': DEFAULT_SHEET_NAME,
            'sheet_rows': EXAMPLE_SHEET_ROWS,
        }

    @classmethod
    def deserialize(cls, rows):
        return cls(rows)

    @classmethod
    def load_from_upload(cls, f):
        try:
            rows = glean_labor_categories_from_file(f)
            return Region3PriceList(rows)
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
