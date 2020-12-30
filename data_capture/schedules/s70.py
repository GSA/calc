import functools
import logging
import xlrd
import re

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .base import (BasePriceList, min_price_validator,
                   hourly_rates_only_validator)
from .spreadsheet_utils import (generate_column_index_map,
                                safe_cell_str_value, ColumnTitle)
from .coercers import (strip_non_numeric, extract_min_education,
                       extract_hour_unit_of_issue, extract_first_int)
from contracts.models import EDUCATION_CHOICES


DEFAULT_SHEET_NAME = '(3)Labor Categories'

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

EXAMPLE_SHEET_ROWS = [
    [
        COLUMN_TITLES['sin'].canonical_name,
        COLUMN_TITLES['labor_category'].canonical_name,
        COLUMN_TITLES['education_level'].canonical_name,
        COLUMN_TITLES['min_years_experience'].canonical_name,
        r'COMMERCIAL LIST PRICE (CPL) OR MARKET PRICES',
        COLUMN_TITLES['unit_of_issue'].canonical_name,
        r'MOST FAVORED CUSTOMER (MFC)',
        r'BEST  DISCOUNT OFFERED TO MFC (%)',
        r'MFC PRICE',
        r'GSA(%) DISCOUNT (exclusive of the .75% IFF)',
        r'PRICE OFFERED TO GSA (excluding IFF)',
        COLUMN_TITLES['price_including_iff'].canonical_name,
        r'QUANTITY/ VOLUME DISCOUNT',
    ],
    [
        r'132-51',
        r'Project Manager',
        r'Bachelors',
        r'5',
        r'$125',
        r'Hour',
        r'All Commercial Customers',
        r'7.00%',
        r'$123.99',
        r'10.00%',
        r'$110.99',
        r'$115.99',
        r'15.00%',
    ]
]

# Text to indicate the definite end of the the price list table
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
    # TODO: I'm not sure how big these uploaded files can get. While
    # the labor categories price lists don't get that long, according to
    # user research interviews, *product* price lists can get really long;
    # and even though we're not interested in them, information about them
    # is embedded in the workbook, so the file could potentially get large.
    #
    # Unfortunately, it doesn't *seem* like xlrd supports file streaming.
    # Although it does support using memory-mapped files, so perhaps that's a
    # possibility.

    book = xlrd.open_workbook(file_contents=f.read())

    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):
    if sheet_name not in book.sheet_names():
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )

    sheet = book.sheet_by_name(sheet_name)

    rownum = find_header_row(sheet) + 1  # add 1 to start on first data row

    cats = []

    heading_row = sheet.row(rownum - 1)

    col_idx_map = generate_column_index_map(heading_row, COLUMN_TITLES)

    # dict of property names to functions that will be used to coerce values
    # if a field is not in this map, it will just be retrieved (safely)
    # as a string
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


class Schedule70Row(forms.Form):
    sin = forms.CharField(label="SIN(s) proposed")
    labor_category = forms.CharField(
        label="Service proposed",
        help_text="e.g. job title/task"
    )
    education_level = forms.CharField(
        label="Min. education",
        help_text="or certification level",
    )
    min_years_experience = forms.IntegerField(
        label="Min. years of experience"
    )
    unit_of_issue = forms.CharField(
        label="Unit of issue",
        validators=[hourly_rates_only_validator]
    )
    price_including_iff = forms.DecimalField(
        label="Price offered to GSA",
        help_text="including IFF",
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


class Schedule70PriceList(BasePriceList):
    title = 'IT Schedule 70'
    table_template = 'data_capture/price_list/tables/schedule_70.html'
    upload_example_template = ('data_capture/price_list/upload_examples/'
                               'schedule_70.html')
    upload_widget_extra_instructions = 'XLS or XLSX format, please.'

    def __init__(self, rows):
        super().__init__()

        self.rows = rows

        for row in self.rows:
            form = Schedule70Row(row)
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
                                 'header': Schedule70Row()})

    def to_error_table(self):
        return render_to_string(self.table_template,
                                {'rows': self.invalid_rows,
                                 'header': Schedule70Row()})

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
            return Schedule70PriceList(rows)
        except ValidationError:
            raise
        except Exception as e:
            logger.info('Failed to glean data from %s: %s' % (f.name, e))

            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
