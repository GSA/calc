import json

from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt

from django.shortcuts import redirect, render
from django.template.loader import render_to_string
from django.http import HttpResponseBadRequest
from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db import transaction
from django.utils import timezone
from django.utils.http import is_safe_url
from django.utils.safestring import mark_safe
from django.utils.html import escape

from .. import forms
from ..models import SubmittedPriceList
from ..decorators import handle_cancel
from ..schedules import registry
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import (add_generic_form_error, build_url,
                     get_nested_item, get_deserialized_gleaned_data)
from .replay import Replayer
from frontend import ajaxform
from frontend.steps import Steps


SESSION_KEY = 'data_capture:price_list'

replayer = Replayer(SESSION_KEY)

steps = Steps(
    template_format='data_capture/price_list/step_{}.html',
    extra_ctx_vars={
        'current_selected_tab': 'upload_price_data'
    },
    extra_ctx_processors=[replayer.context_processor]
)


@csrf_exempt
def get_step_form_from_session(step_number, request, **kwargs):
    '''
    Bring back the given Form instance for a step from the
    request session.  Returns None if the step hasn't been completed yet.

    Any keyword arguments are passed on to the Form constructor.
    '''

    cls = getattr(forms, 'Step{}Form'.format(step_number))
    post_data = get_nested_item(request.session, (
        SESSION_KEY,
        'step_{}_POST'.format(step_number)
    ))
    if post_data is None:
        return None
    form = cls(post_data, **kwargs)
    if not form.is_valid():
        raise AssertionError(
            'invalid step {} data in session'.format(step_number)
        )
    return form


@csrf_exempt
def clear_gleaned_data_if_different_schedule(request):
    # If a different schedule has been chosen from that of the gleaned_data
    # in session, then delete gleaned_data from session so that the upload
    # step will require an upload of data from the newly selected schedule.
    sess = request.session
    new_schedule = request.POST['schedule']
    gleaned_data = get_deserialized_gleaned_data(request)
    if gleaned_data and (registry.get_classname(gleaned_data) !=
                         new_schedule):
        del sess[SESSION_KEY]['gleaned_data']


@csrf_exempt
def tutorial(request):
    from ..schedules.s70 import Schedule70PriceList

    upload_example_info = render_to_string(
        Schedule70PriceList.upload_example_template,
        Schedule70PriceList.get_upload_example_context()
    )

    return render(request, 'data_capture/tutorial.html', {
        'current_selected_tab': 'upload_price_data',
        'upload_example_info': upload_example_info,
    })


@steps.step(label='Basic information')
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel  # This is for canceling a replay.
@csrf_exempt
def step_1(request, step):
    if request.method == 'GET':
        form = forms.Step1Form(data=get_nested_item(
            request.session,
            (SESSION_KEY, 'step_1_POST')
        ))
    else:
        form = forms.Step1Form(request.POST)
        if form.is_valid():
            sess = request.session
            if SESSION_KEY in sess:
                clear_gleaned_data_if_different_schedule(request)
                sess[SESSION_KEY]['step_1_POST'] = request.POST
                sess.save()
            else:
                sess[SESSION_KEY] = {
                    'step_1_POST': request.POST,
                }

            return redirect('data_capture:step_2')
        elif form.has_existing_contract_number_error():
            contract_number = request.POST['contract_number']
            latest = SubmittedPriceList.get_latest_by_contract_number(
                contract_number)
            details_url = build_url('data_capture:price_list_details',
                                    reverse_kwargs={'id': latest.pk})
            msg = mark_safe(  # nosec
                "We found an <a href='{}' target='_blank'>existing price list</a> "
                "for contract number {}.".format(
                    details_url, escape(contract_number)))
            messages.add_message(request, messages.ERROR, msg)
        else:
            add_generic_form_error(request, form)

    return step.render(request, {
        'form': form,
    })


@steps.step(label='Vendor details')
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
@csrf_exempt
def step_2(request, step):
    # Redirect back to step 1 if we don't have data
    if get_step_form_from_session(1, request) is None:
        return redirect('data_capture:step_1')
    else:
        step_1_data = get_step_form_from_session(1, request)

    if request.method == 'GET':
        form = forms.Step2Form(data=get_nested_item(
            request.session,
            (SESSION_KEY, 'step_2_POST')
        ))
    else:
        form = forms.Step2Form(request.POST)
        if form.is_valid():
            session_data = request.session[SESSION_KEY]
            session_data['step_2_POST'] = request.POST

            # Changing the value of a subkey doesn't cause the session to save,
            # so do it manually
            request.session.modified = True

            return redirect('data_capture:step_3')
        else:
            add_generic_form_error(request, form)
    return step.render(request, {
        'form': form,
        'preferred_schedule_title':
            step_1_data.cleaned_data['schedule_class'].title,
        'contract_number': step_1_data.cleaned_data['contract_number']
    })


@steps.step(label='Price list upload')
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
@replayer.recordable
@csrf_exempt
def step_3(request, step, recorder):
    if get_step_form_from_session(2, request) is None:
        return redirect('data_capture:step_2')

    session_pl = request.session[SESSION_KEY]
    step_1_data = get_step_form_from_session(1, request).cleaned_data
    schedule_class = step_1_data['schedule_class']

    gleaned_data = get_deserialized_gleaned_data(request)
    is_file_required = not (gleaned_data and gleaned_data.valid_rows)

    if request.method == 'GET':
        existing_filename = None

        if not is_file_required:
            existing_filename = session_pl.get('filename')

        form = forms.PriceListUploadForm(
            schedule=step_1_data['schedule'],
            is_file_required=is_file_required,
            existing_filename=existing_filename,
        )
    else:  # POST
        gleaned_data = get_deserialized_gleaned_data(request)

        form = forms.PriceListUploadForm(
            request.POST,
            request.FILES,
            schedule=step_1_data['schedule'],
            is_file_required=is_file_required
        )

        if form.is_valid():
            if 'gleaned_data' in form.cleaned_data:
                gleaned_data = form.cleaned_data['gleaned_data']

                session_pl['gleaned_data'] = registry.serialize(gleaned_data)
                session_pl['filename'] = form.cleaned_data['file'].name
                request.session.modified = True

            recorder.on_gleaned_data(gleaned_data)

            if gleaned_data.invalid_rows:
                return ajaxform.redirect(request, 'data_capture:step_3_errors')
            return ajaxform.redirect(request, 'data_capture:step_4')
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context=step.context({
            'form': form,
            'upload_example': schedule_class.render_upload_example(request)
        }, request),
        template_name=step.template_name,
        ajax_template_name='data_capture/price_list/upload_form.html',
    )


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@handle_cancel
@require_http_methods(["GET"])
@csrf_exempt
def step_3_errors(request):
    step = steps.get_step_renderer(3)

    gleaned_data = get_deserialized_gleaned_data(request)

    if gleaned_data is None:
        return redirect('data_capture:step_3')

    step_1_form = get_step_form_from_session(1, request)

    preferred_schedule = step_1_form.cleaned_data['schedule_class']

    form = forms.PriceListUploadForm(
        schedule=step_1_form.cleaned_data['schedule'])

    return render(request,
                  'data_capture/price_list/step_3_errors.html',
                  step.context({
                      'form': form,
                      'gleaned_data': gleaned_data,
                      'is_preferred_schedule': isinstance(gleaned_data,
                                                          preferred_schedule),
                      'preferred_schedule_title': preferred_schedule.title,
                  }, request))


@steps.step(label='Data verification')
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@handle_cancel
@transaction.atomic
@csrf_exempt
def step_4(request, step):
    gleaned_data = get_deserialized_gleaned_data(request)

    if gleaned_data is None:
        return redirect('data_capture:step_3')

    if request.method == 'GET' and not gleaned_data.valid_rows:
        return redirect('data_capture:step_3')

    session_pl = request.session[SESSION_KEY]
    step_1_form = get_step_form_from_session(1, request)
    step_2_form = get_step_form_from_session(2, request)

    pl_details = {
        'preferred_schedule': step_1_form.cleaned_data['schedule_class'],
        'contract_number': step_1_form.cleaned_data['contract_number'],
        'vendor_name': step_2_form.cleaned_data['vendor_name'],
        'is_small_business': step_2_form.cleaned_data['is_small_business'],
        'contractor_site': step_2_form.cleaned_data['contractor_site'],
        'contract_start': step_2_form.cleaned_data['contract_start'],
        'contract_end': step_2_form.cleaned_data['contract_end'],
        'escalation_rate': step_2_form.cleaned_data['escalation_rate'],
    }

    show_edit_form = (request.GET.get('show_edit_form') == 'on')

    if request.method == 'POST':
        if not gleaned_data.valid_rows:
            # Our UI never should've let the user issue a request
            # like this.
            return HttpResponseBadRequest()
        form = forms.Step4Form(request.POST)
    else:
        form = forms.Step4Form.from_post_data_subsets(
            session_pl['step_1_POST'],
            session_pl['step_2_POST']
        )

    prev_url = request.GET.get('prev')
    if not is_safe_url(prev_url):
        prev_url = None

    step_4_without_edit_url = build_url('data_capture:step_4',
                                        prev=prev_url)
    step_4_with_edit_url = build_url('data_capture:step_4',
                                     prev=prev_url,
                                     show_edit_form='on')

    if request.method == 'POST':
        if form.is_valid():
            if 'save-changes' in request.POST:
                # There's not a particularly easy way to separate one
                # step's fields from another, but fortunately that's OK
                # because Django's Form constructors take only the POST
                # data they need, and ignore the rest.
                session_pl['step_1_POST'] = request.POST
                session_pl['step_2_POST'] = request.POST

                # Changing the value of a subkey doesn't cause the session to
                # save, so do it manually.
                request.session.modified = True

                return redirect(step_4_without_edit_url)
            else:
                price_list = form.save(commit=False)

                price_list.submitter = request.user
                price_list.serialized_gleaned_data = json.dumps(
                    session_pl['gleaned_data'])

                # We always want to explicitly set the schedule to the
                # one that the gleaned data is part of, in case we gracefully
                # fell back to a schedule other than the one the user chose.
                price_list.schedule = registry.get_classname(gleaned_data)

                price_list.status = SubmittedPriceList.STATUS_UNREVIEWED
                price_list.status_changed_at = timezone.now()
                price_list.status_changed_by = request.user

                price_list.uploaded_filename = session_pl['filename']

                price_list.save()
                gleaned_data.add_to_price_list(price_list)

                del request.session[SESSION_KEY]

                return redirect('data_capture:step_5')
        else:
            add_generic_form_error(request, form)
            show_edit_form = True

    return step.render(request, {
        'show_edit_form': show_edit_form,
        'form': form,
        'step_4_with_edit_url': step_4_with_edit_url,
        'step_4_without_edit_url': step_4_without_edit_url,
        'prev_url': prev_url,
        'gleaned_data': gleaned_data,
        'price_list': pl_details,
        'is_preferred_schedule': isinstance(gleaned_data,
                                            pl_details['preferred_schedule']),
        'preferred_schedule_title': pl_details['preferred_schedule'].title,
    })


@steps.step(label='Complete')
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@csrf_exempt
def step_5(request, step):
    return step.render(request)
