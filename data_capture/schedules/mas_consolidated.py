import xlrd
import functools

from django import forms
from django.core.exceptions import ValidationError
from django.template.loader import render_to_string

from .base import (BasePriceList, hourly_rates_only_validator,
                   min_price_validator)
from .spreadsheet_utils import safe_cell_str_value  # generate_column_index_map_mas
from .coercers import (strip_non_numeric, extract_min_education,
                       extract_hour_unit_of_issue)
from contracts.models import EDUCATION_CHOICES

DEFAULT_SHEET_NAME = 'Services Pricing'

Keywords = 'Key Words*(separated by commas, limit to five keywords.\
            include these words in the description)'
Desc = 'Recognized as a subject matter expert with extensive experience... '
EXAMPLE_SHEET_ROWS = [
    [
        r'Vendor Name*',
        r'SIN/SIN(s) Proposed*',
        r'Service Proposed  (eg Job Title/Task)*',
        r'Description(250 words)*',
        Keywords,
        r'Minimum Education',
        r'Minimum Years of Experience (cannot be a range)',
        r'Identify Required Licenses or Certifications (State "None" if not required)',
        r'Security Clearance Required',
        r'Contractor or Customer Facility or Both*',
        r'Domestic or Overseas*',
        r'Commercial Price List (CPL) OR Market Prices*',
        r'Unit of Issue (e.g. Hour, Task, Sq Ft)*',
        r'Most Favored Commercial Customer (MFC)*',
        r'Discount Offered to Commercial MFC (%)*',
        r'Commercial MFC Price*',
        r'Discount Offered to GSA (off CPL or Market Prices) (%)',
        r'Discount Offered to GSA (off MFC Prices) (%)*',
        r'Price Offered to GSA (Excluding IFF)*',
        r'Price Offered to GSA (including IFF)',
        r'Supporting Invoice or Document Number(Initial submittal)*',
    ],
    [
        r'XYZ,INC',
        r'874-1',
        r'Principal Consultant',
        Desc,
        r'Process improvement, finance, senior project manager',
        r'Bachelors',
        r'10',
        r'PMP',
        r'No',
        r'Both',
        r'Domestic',
        r'Market',
        r'Hour',
        r'',
        r'',
        r'0.00',
        r'',
        r'',
        r'0.00',
        r'200.00',
        r'',
    ],
]


DEFAULT_FIELD_TITLE_MAP_MAS = {
    'sin': 'SIN/SIN(s) Proposed',
    'labor_category': 'Service Proposed',
    'education_level': 'Minimum Education',
    'min_years_experience': 'Minimum Years of Experience',
    'unit_of_issue': 'Unit of Issue',
    'price_including_iff': 'Price Offered',
    'keywords': 'Key words',
    'certifications': 'Identify Required Licenses or Certifications',
    'security_clearance': 'Security Clearance Required'
}

# columnIndex = [1,2,5,6,12,19,4,7,8]
columnIndex = {'sin': 1, 'labor_category': 2, 'education_level': 5, 'min_years_experience': 6,
               'unit_of_issue': 12, 'price_including_iff': 19, 'keywords': 4,
               'certifications': 7, 'security_clearance': 8}


def glean_labor_categories_from_file(f, sheet_name=DEFAULT_SHEET_NAME):
    book = xlrd.open_workbook(file_contents=f.read())
    return glean_labor_categories_from_book(book, sheet_name)


def glean_labor_categories_from_book(book, sheet_name=DEFAULT_SHEET_NAME):
    sheetNameList = [sheetName.lower().strip() for sheetName in book.sheet_names()]
    if sheet_name.lower() not in sheetNameList:
        raise ValidationError(
            'There is no sheet in the workbook called "%s".' % sheet_name
        )
    else:
        sheetIndex = sheetNameList.index(sheet_name.lower())

    sheet = book.sheet_by_name(book.sheet_names()[sheetIndex])

    rownum = 1  # start on first row after heading row

    cats = []

    # heading_row = sheet.row(0)
    # col_idx_map = generate_column_index_map_mas(heading_row,DEFAULT_FIELD_TITLE_MAP_MAS)
    col_idx_map = columnIndex
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


class MASConsolidatedPriceListRow(forms.Form):
    sin = forms.CharField(label='SIN/SIN(s) Proposed')
    labor_category = forms.CharField(
        label="SERVICE PROPOSED (eg Job Title/Task)"
    )
    keywords = forms.CharField(
        label='Key Words',
        required=False
    )
    security_clearance = forms.CharField(
        label='Security Clearance Required',
        required=False
    )
    education_level = forms.CharField(
        label="Minimum Education"
    )
    min_years_experience = forms.IntegerField(
        label="Minimum Years of Experience (cannot be a range)"
    )
    certifications = forms.CharField(
        label='Identify Required Licenses or Certifications',
        required=False
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


class MASConsolidatedPriceList(BasePriceList):

    title = 'MAS Consolidated'

    table_template = 'data_capture/price_list/tables/MAS_Consolidated.html'

    upload_example_template = ('data_capture/price_list/upload_examples/'
                               'MAS_Consolidated.html')

    upload_widget_extra_instructions = 'XLS or XLSX format, please.'

    def __init__(self, rows):
        super().__init__()
        self.rows = rows
        for row in self.rows:
            form = MASConsolidatedPriceListRow(row)
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
                sin=row.cleaned_data['sin'],
                keywords=row.cleaned_data['keywords'],
                certifications=row.cleaned_data['certifications'],
                security_clearance=row.cleaned_data['security_clearance']
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
            return MASConsolidatedPriceList(rows)
        except ValidationError:
            raise
        except Exception as e:
            raise ValidationError(
                "An error occurred when reading your Excel data."
            )
