import json

from functools import wraps
from django.db import transaction
from django.http import HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import SuspiciousOperation

from .common import (add_generic_form_error, get_nested_item,
                     get_deserialized_gleaned_data, add_change_success_message)
from .. import forms
from ..schedules import registry
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from frontend import ajaxform
from frontend.steps import Steps


SESSION_KEY = 'data_capture:replace_price_list'

steps = Steps(
    template_format='data_capture/replace_price_list/replace_step_{}.html'
)


def session_id_required(view_func):
    '''
    Decorator to enforce that the Price List <id> passed to the view function
    matches the one currently in session. This is used to prevent someone
    fudging with form actions.
    '''
    @wraps(view_func)
    def _session_id_required(request, *args, **kwargs):
        id = kwargs.get('id')
        id_session = get_nested_item(request.session,
                                     (SESSION_KEY, 'price_list_id'))
        if not id_session:
            # redirect if session doesn't contain an id at all
            return redirect('data_capture:price_list_details', id=id)
        if id != id_session:
            # something fishy is going on if the id URL parameter doesn't
            # match the one in session, so raise an exception
            raise SuspiciousOperation()

        return view_func(request, *args, **kwargs)

    return _session_id_required


def handle_replace_cancel(view_func):
    '''
    If 'cancel' is POSTed to the decorated function, clear out the session
    and redirect back to the details page
    '''
    @wraps(view_func)
    def _handle_replace_cancel(request, *args, **kwargs):
        if request.method == 'POST' and 'cancel' in request.POST:
            id = kwargs.get('id')
            del request.session[SESSION_KEY]
            return redirect('data_capture:price_list_details', id=id)

        return view_func(request, *args, **kwargs)

    return _handle_replace_cancel


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
def replace_step_1(request, id, step):
    price_list = price_list = get_object_or_404(SubmittedPriceList, pk=id)
    schedule_class = registry.get_class(price_list.schedule)

    if request.method == 'GET':
        form = forms.PriceListUploadForm(schedule=price_list.schedule)
    else:  # POST
        form = forms.PriceListUploadForm(request.POST,
                                         request.FILES,
                                         schedule=price_list.schedule)
        if form.is_valid():
            gleaned_data = form.cleaned_data['gleaned_data']
            request.session[SESSION_KEY] = {
                'gleaned_data': registry.serialize(gleaned_data),
                'uploaded_filename': form.cleaned_data['file'].name,
                # save the id in session to make sure flow is not messed with
                'price_list_id': id,
            }

            if gleaned_data.invalid_rows:
                return ajaxform.redirect(request,
                                         'data_capture:replace_step_1_errors',
                                         id=price_list.pk)
            return ajaxform.redirect(request,
                                     'data_capture:replace_step_2',
                                     id=price_list.pk)
        else:
            add_generic_form_error(request, form)

    return ajaxform.render(
        request,
        context=step.context({
            'form': form,
            'price_list': price_list,
            'upload_example': schedule_class.render_upload_example(request),
        }),
        template_name=step.template_name,
        ajax_template_name='data_capture/replace_price_list/upload_form.html',
    )


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@session_id_required
@handle_replace_cancel
@require_http_methods(["GET"])
def replace_step_1_errors(request, id):
    step = steps.get_step_renderer(1)
    price_list = price_list = get_object_or_404(SubmittedPriceList, pk=id)

    gleaned_data = get_deserialized_gleaned_data(
        request, primary_session_key=SESSION_KEY)

    if gleaned_data is None:
        return redirect('data_capture:replace_step_1', id=price_list.pk)

    form = forms.PriceListUploadForm(schedule=price_list.schedule)

    return render(request,
                  'data_capture/replace_price_list/replace_step_1_errors.html',
                  step.context({
                      'form': form,
                      'price_list': price_list,
                      'gleaned_data': gleaned_data,
                  }))


@steps.step
@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@require_http_methods(["GET", "POST"])
@session_id_required
@handle_replace_cancel
@transaction.atomic
def replace_step_2(request, id, step):
    price_list = price_list = get_object_or_404(SubmittedPriceList, pk=id)

    gleaned_data = get_deserialized_gleaned_data(
        request, primary_session_key=SESSION_KEY)

    if gleaned_data is None:
        return redirect('data_capture:replace_step_1', id=price_list.pk)

    if request.method == 'GET' and not gleaned_data.valid_rows:
        return redirect('data_capture:replace_step_1', id=price_list.pk)

    if request.method == 'POST':
        if not gleaned_data.valid_rows:
            # Our UI never should've let the user issue a request like this
            return HttpResponseBadRequest()

        price_list.submitter = request.user
        price_list.uploaded_filename = request.session[SESSION_KEY][
            'uploaded_filename']

        price_list.serialized_gleaned_data = json.dumps(
            registry.serialize(gleaned_data))

        # delete the old rows
        price_list.rows.all().delete()

        # set to STATUS_UNREVIEWED and delete associated Contracts
        price_list.unreview(request.user)

        # add the new rows
        gleaned_data.add_to_price_list(price_list)

        # clear out session
        del request.session[SESSION_KEY]

        add_change_success_message(request)

        return redirect('data_capture:price_list_details', id=price_list.pk)

    return step.render(request, {
        'price_list': price_list,
        'gleaned_data': gleaned_data,
    })
