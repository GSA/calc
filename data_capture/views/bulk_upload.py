from django.shortcuts import redirect
from django.core.files.base import ContentFile
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.contrib.auth.decorators import login_required, permission_required
from django.template.loader import render_to_string

from django.views.decorators.csrf import csrf_exempt

from .. import forms, jobs
from ..r10_spreadsheet_converter import Region10SpreadsheetConverter
from ..management.commands.initgroups import BULK_UPLOAD_PERMISSION
from ..decorators import handle_cancel
from .common import add_generic_form_error
from frontend import ajaxform
from frontend.steps import Steps
from contracts.models import BulkUploadContractSource


steps = Steps(
    template_format='data_capture/bulk_upload/region_10_step_{}.html',
)

EXAMPLE_SHEET_ROWS = [
    [
        'Labor Category',
        'Year 1/base',
        'Year 2',
        'Year 3',
        'Year 4',
        'Year 5',
        'Education',
        'MinExpAct',
        'Bus Size',
        'Location',
        'COMPANY NAME',
        'CONTRACT .',
        'Schedule',
        'SIN NUMBER',
        'Begin Date',
        'End Date',
        'Contract Year',
    ],
    [
        'Academic Expert',
        '580.69',
        '592.30',
        '604.14',
        '616.23',
        '628.55',
        'Ph.D.',
        '5',
        'S',
        'Both',
        'Acme Inc.',
        'GS-000-1234',
        'Consolidated',
        '123-45',
        '5/1/16',
        '4/30/20',
        '1',
    ]
]


def render_r10_spreadsheet_example(request=None):
    return render_to_string(
        'data_capture/price_list/upload_examples/region_10_bulk.html',
        {'sheet_rows': EXAMPLE_SHEET_ROWS},
        request=request)


@csrf_exempt
@steps.step(label='Upload spreadsheet')
@login_required
@permission_required(BULK_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
def bulk_region_10_step_1(request, step):
    '''
    Start of Region 10 Bulk Upload - Upload the spreadsheet
    '''
    if request.method == 'GET':
        form = forms.Region10BulkUploadForm()
    elif request.method == 'POST':
        form = forms.Region10BulkUploadForm(request.POST, request.FILES)

        if form.is_valid():
            file = form.cleaned_data['file']

            upload_source = BulkUploadContractSource.objects.create(
                submitter=request.user,
                procurement_center=BulkUploadContractSource.REGION_10,
                has_been_loaded=False,
                original_file=file.read(),
                file_mime_type=file.content_type
            )

            request.session['data_capture:upload_source_id'] = upload_source.pk

            return ajaxform.redirect(
                request,
                'data_capture:bulk_region_10_step_2'
            )
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context=step.context({
            'form': form,
            'upload_example': render_r10_spreadsheet_example(request),
        }),
        template_name=step.template_name,
        ajax_template_name='data_capture/bulk_upload/'
                           'region_10_step_1_form.html',
    )


@csrf_exempt
@steps.step(label='Confirm load')
@login_required
@permission_required(BULK_UPLOAD_PERMISSION, raise_exception=True)
@handle_cancel
@require_http_methods(["GET", "POST"])
def bulk_region_10_step_2(request, step):
    '''
    Confirm that the new data should be loaded and load it when the user
    submits
    '''
    upload_source_id = request.session.get('data_capture:upload_source_id')
    if upload_source_id is None:
        return redirect('data_capture:bulk_region_10_step_1')

    if request.method == 'GET':
        # Get the BulkUploadContractSource based on upload_source_id
        upload_source = BulkUploadContractSource.objects.get(
            pk=upload_source_id)

        file = ContentFile(upload_source.original_file)

        file_metadata = Region10SpreadsheetConverter(file).get_metadata()

        return step.render(request, {
            'file_metadata': file_metadata,
        })

    # else 'POST' because of @require_http_methods decorator
    jobs.process_bulk_upload_and_send_email.delay(upload_source_id)

    # remove the upload_source_id from session
    del request.session['data_capture:upload_source_id']

    return redirect('data_capture:bulk_region_10_step_3')


@csrf_exempt
@steps.step(label='Complete')
@login_required
@permission_required(BULK_UPLOAD_PERMISSION, raise_exception=True)
def bulk_region_10_step_3(request, step):
    '''Show success page'''

    return step.render(request, {
        'SEND_TRANSACTIONAL_EMAILS': settings.SEND_TRANSACTIONAL_EMAILS,
    })
