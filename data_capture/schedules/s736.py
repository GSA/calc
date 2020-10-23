import functools
import logging
import re
import xlrd


from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .base import (BasePriceList, hourly_rates_only_validator,
                   min_price_validator)
from .spreadsheet_utils import (ColumnTitle, generate_column_index_map,
                                safe_cell_str_value)
from .coercers import (strip_non_numeric, extract_first_int,
                       extract_min_education, extract_hour_unit_of_issue)
from contracts.models import EDUCATION_CHOICES


DEFAULT_SHEET_NAME = 'Professional Market Prce Escala'

EXAMPLE_SHEET_ROWS = [
    [
        r'SIN PROPOSED',
        r'SERVICE PROPOSED',
        r'MINIMUM EDUCATION/CERTIFICATION LEVEL',
        r'MINIMUM YEARS OF EXPERIENCE',
        r'MARKET RATE',
        r'UNIT OF ISSUE (e.g. Hour)',
        r'MOST FAVORED COMMERCIAL CUSTOMER (MFC) **',
        r'DISCOUNT OFFERED TO COMMERCIAL MFC (%)',
        r'COMMERCIAL MFC PRICE',
        r'MOST FAVORED FEDERAL AGENCY (MFC)***',
        r'DISCOUNT OFFERED TO MOST FAVORED FEDERAL AGENCY (MFC) ***',
        r'MOST FAVORED FEDERAL AGENCY (MFC) PRICE***',
        r'DISCOUNT OFFERED TO GSA (%)',
        r'PRICED OFFERED TO GSA (excluding IFF)*',
        r'PRICED OFFERED TO GSA (includingIFF)*',
        r'Annual Escalation Rate Proposed',
        r'PRICED OFFERED TO GSA (includingIFF)* Year 1',
        r'PRICED OFFERED TO GSA (includingIFF)* Year 2',
        r'PRICED OFFERED TO GSA (includingIFF)* Year 3',
        r'PRICED OFFERED TO GSA (includingIFF)* Year 4',
        r'PRICED OFFERED TO GSA (includingIFF)* Year 5',
    ],
    [
        r'736-5',
        r'Junior Analyst',
        r'Bachelors',
        r'2',
        r'$50.00',
        r'Hour',
        r'ABC Corp',
        r'0%',
        r'$50.00',
        r'XYZ Agency',
        r'15%',
        r'$42.50',
        r'15%',
        r'$42.50',
        r'$42.82',
        r'2%',
        r'$42.82',
        r'$43.68',
        r'$44.55',
        r'$45.44',
        r'$46.35',
    ],
]

COLUMN_TITLES = {
    'sin': ColumnTitle(
        canonical_name=r'SIN(s) PROPOSED',
        alternatives=[
            re.compile(r'SIN.*')
        ]
    ),
    'labor_category': ColumnTitle(
        canonical_name=r'SERVICE PROPOSED (e.g. Job Title/Task)',
        alternatives=['Labor Categories'],
    ),
    'education_level': ColumnTitle(
        canonical_name=r'MINIMUM EDUCATION/ CERTIFICATION LEVEL',
        alternatives=['MINIMUM EDUCATION']
    ),
    'min_years_experience': ColumnTitle(
        canonical_name=r'MINIMUM YEARS OF EXPERIENCE',
        alternatives=['Years of experience'],
    ),
    'unit_of_issue': ColumnTitle(
        canonical_name=r'UNIT OF ISSUE (e.g. Hour, Task, Sq ft)'
    ),
    'price_including_iff': ColumnTitle(
        canonical_name=r'PRICE OFFERED TO GSA (including IFF)'
    ),
}

DEFAULT_FIELD_TITLE_MAP = {
    'sin': 'SIN PROPOSED',
    'labor_category': 'SERVICE PROPOSED',  # noqa
    'education_level': 'MINIMUM EDUCATION/CERTIFICATION LEVEL',
    'min_years_experience': 'MINIMUM YEARS OF EXPERIENCE',
    'unit_of_issue': 'UNIT OF ISSUE (e.g. Hour)',
    'price_including_iff': 'PRICED OFFERED TO GSA (includingIFF)*',
}

STOP_TEXT = r'Most Favored Customer'

logger = logging.getLogger('calc')


def find_header_row(sheet, row_threshold=50):
    first_col_heading = COLUMN_TITLES['sin']
    row_limit = min(sheet.nrows, row_threshold)

    for rx in range(row_limit):
        val = sheet.cell_value(rx, 0)
        if isinstance(val, str) and first_col_heading.matches(val):
            return rx

    raise ValidationError(
        'Could not find the column {}.'.format(first_col_heading)
    )


def glean_labor_categories_from_file(f, sheet_name=DEFAULT_SHEET_NAME):
    book = xlrd.open_workbook(file_contents=f.read())
    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):
    # TODO: This should be DRY'd out a bit since it is extremely similar
    # to the s70.py function of the same name.

    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    rownum = find_header_row(sheet) + 1  # add 1 to start on first data row

    cats = []

    heading_row = sheet.row(rownum - 1)

    col_idx_map = generate_column_index_map(heading_row,
                                            DEFAULT_FIELD_TITLE_MAP)

    coercion_map = {
        'price_including_iff': strip_non_numeric,
        'min_years_experience': extract_first_int,
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

        has_stop_text = re.match(STOP_TEXT, cval(0), re.IGNORECASE)

        # We just keep going until we run into a row that either starts with
        # STOP_TEXT or that doesn't have a SIN and price including IFF.
        should_stop = has_stop_text or (
            not sin.strip() and not price_including_iff.strip())

        if should_stop:
            break

        cat = {}

        for field, col_idx in col_idx_map.items():
            coercer = coercion_map.get(field, None)
            cat[field] = cval(col_idx, coercer=coercer)

        cats.append(cat)

        rownum += 1

    return cats


class Schedule736PriceListRow(forms.Form):
    sin = forms.CharField(label='SIN PROPOSED')
    labor_category = forms.CharField(
        label="SERVICE PROPOSED"
    )
    education_level = forms.CharField(
        label="MINIMUM EDUCATION/CERTIFICATION LEVEL"
    )
    min_years_experience = forms.IntegerField(
        label="MINIMUM YEARS OF EXPERIENCE"
    )
    unit_of_issue = forms.CharField(
        label="UNIT OF ISSUE (e.g. Hour)",
        validators=[hourly_rates_only_validator]
    )
    price_including_iff = forms.DecimalField(
        label='PRICED OFFERED TO GSA (includingIFF)*',
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


class Schedule736PriceList(BasePriceList):
    # TODO: This class should be DRY'd out since it is nearly verbatim
    # from the Schedule70PriceList class, but since this feature
    # is somewhat experimental, I'm focusing more on implementation speed

    title = 'Schedule 736 TAPS'  # TODO: unsure of title

    table_template = 'data_capture/price_list/tables/s736.html'

    # TODO: create the upload example template
    upload_example_template = ('data_capture/price_list/upload_examples/'
                               's736.html')
    upload_widget_extra_instructions = 'XLS or XLSX format, please.'

    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        for row in self.rows:
            form = Schedule736PriceListRow(row)
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
                                {'rows': self.valid_rows,
                                 'header': Schedule736PriceListRow()})

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
            return Schedule736PriceList(rows)
        except ValidationError:
            raise
        except Exception as e:
            logger.info('Failed to glean data from %s: %s' % (f.name, e))

            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
