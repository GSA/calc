import json

from django.db import transaction
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages

from .. import forms
from ..schedules import registry
from ..models import SubmittedPriceList
from ..management.commands.initgroups import PRICE_LIST_UPLOAD_PERMISSION
from .common import (add_generic_form_error, build_url,
                     add_change_success_message)


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
def list_price_lists(request):
    '''
    This view lists a user's SubmittedPriceLists, segmented into lists based
    on the model's status.
    '''
    approved_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_APPROVED).order_by(
            '-status_changed_at')

    unreviewed_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_UNREVIEWED).order_by(
            '-status_changed_at')

    rejected_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_REJECTED).order_by(
            '-status_changed_at')

    retired_price_lists = SubmittedPriceList.objects.filter(
        submitter=request.user,
        status=SubmittedPriceList.STATUS_RETIRED).order_by(
            '-status_changed_at')

    return render(request, 'price_lists/list.html', {
        'approved_price_lists': approved_price_lists,
        'unreviewed_price_lists': unreviewed_price_lists,
        'rejected_price_lists': rejected_price_lists,
        'retired_price_lists': retired_price_lists,
    })


@login_required
@permission_required(PRICE_LIST_UPLOAD_PERMISSION, raise_exception=True)
@transaction.atomic
def price_list_details(request, id):
    '''
    This view shows all the details of a SubmittedPriceList model.
    Note that any logged-in user with the PRICE_LIST_UPLOAD_PERMISSION (so
    Contract Officers and above) can view the page for ANY SubmittedPriceList,
    not just the ones they've submitted.
    '''
    price_list = get_object_or_404(SubmittedPriceList, pk=id)

    gleaned_data = registry.deserialize(
        json.loads(price_list.serialized_gleaned_data))

    pl_rows = price_list.rows.all()

    show_edit_form = (request.GET.get('show_edit_form') == 'on')

    details_without_edit_url = build_url('data_capture:price_list_details',
                                         reverse_kwargs={'id': id})
    details_with_edit_url = build_url('data_capture:price_list_details',
                                      reverse_kwargs={'id': id},
                                      show_edit_form='on')

    if request.method == 'POST':
        form = forms.PriceListDetailsForm(request.POST)
        if form.is_valid():
            # check to make sure something was actually changed
            if not form.is_different_from(price_list):
                messages.add_message(
                    request,
                    messages.INFO,
                    "This price list has not been modified because no changes "
                    "were found in the submitted form."
                )
            else:
                # otherwise, update the price list
                # Update the submitter to the user that made this request
                price_list.submitter = request.user

                # Update the price list's fields to those in the form
                forms.PriceListDetailsForm(
                    request.POST,
                    instance=price_list).save(commit=False)

                # Mark the price list as unreviewed
                price_list.unreview(request.user)  # unreview also saves

                add_change_success_message(request)
            # redirect back either way
            return redirect('data_capture:price_list_details',
                            id=price_list.pk)
        else:
            add_generic_form_error(request, form)
            show_edit_form = True
    else:
        form = forms.PriceListDetailsForm(instance=price_list)

    return render(request, 'price_lists/details.html', {
        'price_list': price_list,
        'gleaned_data': gleaned_data,
        'price_list_rows': pl_rows,
        'details_without_edit_url': details_without_edit_url,
        'details_with_edit_url': details_with_edit_url,
        'show_edit_form': show_edit_form,
        'form': form,
    })
