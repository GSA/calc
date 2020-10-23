from django.contrib.auth.decorators import login_required, permission_required
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect, render

from .common import (add_generic_form_error,
                     get_nested_item, get_deserialized_gleaned_data)
from .. import forms
from ..decorators import handle_cancel
from ..management.commands.initgroups import ANALYZE_PRICES_PERMISSION
from frontend import ajaxform
from frontend.steps import Steps
from ..schedules import registry
from ..analysis.core import analyze_gleaned_data
from ..analysis.export import AnalysisExport

steps = Steps(
    template_format='data_capture/analyze_price_list/step_{}.html',
    extra_ctx_vars={
        'current_selected_tab': 'analyze_price_data'
    },
)


class AnalyzeStep1Form(forms.Step1Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        del self.fields['contract_number']


@steps.step(label='Select a schedule')
@login_required
@permission_required(ANALYZE_PRICES_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
def analyze_step_1(request, step):
    if request.method == 'GET':
        form = AnalyzeStep1Form(data=get_nested_item(
            request.session,
            ('data_capture:analyze_price_list', 'step_1_POST')
        ))
    else:
        form = AnalyzeStep1Form(request.POST)
        if form.is_valid():
            request.session['data_capture:analyze_price_list'] = {
                'step_1_POST': request.POST,
            }

            return redirect('data_capture:analyze_step_2')
        else:
            add_generic_form_error(request, form)

    return step.render(request, {
        'form': form,
    })


@steps.step(label='Upload a price list to analyze')
@login_required
@permission_required(ANALYZE_PRICES_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
def analyze_step_2(request, step):
    step_1_post_data = get_nested_item(request.session, (
        'data_capture:analyze_price_list',
        'step_1_POST'
    ))
    if step_1_post_data is None:
        return redirect('data_capture:analyze_step_1')
    step_1_form = AnalyzeStep1Form(step_1_post_data)
    if not step_1_form.is_valid():
        raise AssertionError('invalid step 1 data in session')
    schedule_class = step_1_form.cleaned_data['schedule_class']
    form_kwargs = dict(
        schedule=step_1_form.cleaned_data['schedule'],
    )

    if request.method == 'GET':
        form = forms.PriceListUploadForm(**form_kwargs)
    else:
        form = forms.PriceListUploadForm(
            request.POST,
            request.FILES,
            **form_kwargs
        )
        if form.is_valid():
            if 'gleaned_data' in form.cleaned_data:
                gleaned_data = form.cleaned_data['gleaned_data']

                session_pl = request.session['data_capture:analyze_price_list']
                session_pl['gleaned_data'] = registry.serialize(gleaned_data)
                session_pl['filename'] = form.cleaned_data['file'].name
                request.session.modified = True

            if gleaned_data.invalid_rows:

                return ajaxform.redirect(request, 'data_capture:analyze_step_2_errors')

            return ajaxform.redirect(request, 'data_capture:analyze_step_3')
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context=step.context({
            'form': form,
            'upload_example': schedule_class.render_upload_example(request)
        }),
        template_name=step.template_name,
        ajax_template_name='data_capture/analyze_price_list/upload_form.html',
    )


@require_http_methods(["GET"])
def analyze_step_2_errors(request):
    step = steps.get_step_renderer(2)

    gleaned_data = get_deserialized_gleaned_data(
        request,
        'data_capture:analyze_price_list'
    )

    if gleaned_data is None:
        return redirect('data_capture:analyze_step_2')

    step_1_post_data = get_nested_item(request.session, (
        'data_capture:analyze_price_list',
        'step_1_POST'
    ))

    step_1_form = AnalyzeStep1Form(step_1_post_data)
    if not step_1_form.is_valid():
        raise AssertionError('invalid step 1 data in session')

    form_kwargs = dict(
        schedule=step_1_form.cleaned_data['schedule'],
    )

    form = forms.PriceListUploadForm(**form_kwargs)

    return render(request,
                  'data_capture/analyze_price_list/step_2_errors.html',
                  step.context({
                      'form': form,
                      'gleaned_data': gleaned_data,
                  }, request))


@steps.step(label='Analysis')
@login_required
@permission_required(ANALYZE_PRICES_PERMISSION, raise_exception=True)
@require_http_methods(["GET"])
def analyze_step_3(request, step):
    gleaned_data = get_deserialized_gleaned_data(
        request,
        'data_capture:analyze_price_list'
    )

    analyzed_rows = analyze_gleaned_data(gleaned_data)

    return step.render(request, {
        'gleaned_data': gleaned_data,
        'analyzed_rows': analyzed_rows,
    })


@require_http_methods(["GET"])
@login_required
@permission_required(ANALYZE_PRICES_PERMISSION, raise_exception=True)
def export_analysis(request):
    gleaned_data = get_deserialized_gleaned_data(
        request,
        'data_capture:analyze_price_list'
    )
    if gleaned_data is None:
        return redirect('data_capture:analyze_step_2')

    format = request.GET.get('f', 'csv')

    # TODO: It'd be nice to cache the analysis from step 3, if possible.
    analyzed_rows = analyze_gleaned_data(gleaned_data)

    analysis_export = AnalysisExport(analyzed_rows)

    file_name_prefix = 'analysis'

    if format == 'xlsx':
        return analysis_export.to_xlsx(filename=file_name_prefix + '.xlsx')
    else:
        return analysis_export.to_csv(filename=file_name_prefix + '.csv')
