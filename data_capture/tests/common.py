import os
import unittest
from copy import deepcopy

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from django.contrib.auth.models import User

from calc.tests.common import ProtectedViewTestCase
from contracts.models import BulkUploadContractSource


def path(*paths):
    root_dir = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
    return os.path.join(root_dir, *paths)


FAKE_SCHEDULE = 'data_capture.schedules.fake_schedule.FakeSchedulePriceList'

FAKE_SCHEDULE_EXAMPLE_PATH = path(
    'static', 'data_capture', 'fake_schedule_example.csv'
)

R10_XLSX_PATH = path('static', 'data_capture', 'r10_export_sample.xlsx')

XLSX_CONTENT_TYPE = ('application/vnd.openxmlformats-'
                     'officedocument.spreadsheetml.sheet')


class FakeCell:
    def __init__(self, val):
        self._val = val

    @property
    def value(self):
        return self._val


class FakeSheet():
    def __init__(self, name, cells):
        self.name = name
        self._cells = deepcopy(cells)

    @property
    def nrows(self):
        return len(self._cells)

    def cell_value(self, rownum, colnum):
        return self._cells[rownum][colnum]

    def row(self, rownum):
        return [FakeCell(c) for c in self._cells[rownum]]


class FakeWorkbook:
    def __init__(self, sheets):
        self._sheets = sheets

    def sheet_names(self):
        return [sheet.name for sheet in self._sheets]

    def sheet_by_name(self, name):
        return [sheet for sheet in self._sheets if sheet.name == name][0]


def uploaded_xlsx_file(path, content=None):
    if content is None:
        with open(path, 'rb') as f:
            content = f.read()

    return SimpleUploadedFile(
        'foo.xlsx',
        content,
        content_type=XLSX_CONTENT_TYPE
    )


def create_bulk_upload_contract_source(user, **kwargs):
    if isinstance(user, str):
        user = User.objects.create_user('testuser', email=user)

    with open(R10_XLSX_PATH, 'rb') as f:
        final_kwargs = dict(
            submitter=user,
            has_been_loaded=False,
            original_file=f.read(),
            file_mime_type=XLSX_CONTENT_TYPE,
            procurement_center=BulkUploadContractSource.REGION_10,
        )
        final_kwargs.update(kwargs)
        return BulkUploadContractSource(**final_kwargs)


def uploaded_csv_file(content=None):
    if content is None:
        with open(FAKE_SCHEDULE_EXAMPLE_PATH, 'rb') as f:
            content = f.read()

    return SimpleUploadedFile(
        'foo.csv',
        content,
        content_type='text/csv'
    )


def create_csv_content(rows=None):
    if rows is None:
        rows = [
            ['132-40', 'Project Manager', 'Bachelors', '7', '15.00']
        ]
    headers = ['sin', 'service', 'education', 'years_experience', 'price']
    all_rows = [headers] + rows
    as_str = '\n'.join([','.join(x) for x in all_rows])
    return as_str.encode('utf-8')


def r10_file(content=None, name='r10.xlsx'):
    if content is None:
        with open(R10_XLSX_PATH, 'rb') as f:
            content = f.read()

    if type(content) is str:
        content = bytes(content, 'UTF-8')

    return SimpleUploadedFile(name, content,
                              content_type=XLSX_CONTENT_TYPE)


@override_settings(
    DATA_CAPTURE_SCHEDULES=[FAKE_SCHEDULE],
)
class StepTestCase(ProtectedViewTestCase):
    def test_permission_is_required(self):
        if not self.url:
            raise unittest.SkipTest()
        super().login()
        res = self.client.get(self.url)
        self.assertEqual(res.status_code, 403)
