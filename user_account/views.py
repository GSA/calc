from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from data_capture.models import SubmittedPriceList


@login_required
def index(request):
    user = request.user

    MAX_RECENT = 5

    total_approved = SubmittedPriceList.objects.filter(
        submitter=user, status=SubmittedPriceList.STATUS_APPROVED).count()
    total_unreviewed = SubmittedPriceList.objects.filter(
        submitter=user, status=SubmittedPriceList.STATUS_UNREVIEWED).count()
    total_rejected = SubmittedPriceList.objects.filter(
        submitter=user, status=SubmittedPriceList.STATUS_REJECTED).count()

    total_submitted = SubmittedPriceList.objects.filter(submitter=user).count()

    recently_approved_price_lists = SubmittedPriceList.objects.filter(
        submitter=user, status=SubmittedPriceList.STATUS_APPROVED).order_by(
            '-status_changed_at')[:MAX_RECENT]

    # TODO: this list is actually both newly created and newly modified
    # Should there be a differentiation?
    recently_submitted_price_lists = SubmittedPriceList.objects.filter(
        submitter=user, status=SubmittedPriceList.STATUS_UNREVIEWED).order_by(
            '-status_changed_at')[:MAX_RECENT]

    return render(request, 'account.html', {
        'total_approved': total_approved,
        'total_unreviewed': total_unreviewed,
        'total_rejected': total_rejected,
        'total_submitted': total_submitted,
        'recently_approved_price_lists': recently_approved_price_lists,
        'recently_submitted_price_lists': recently_submitted_price_lists,
    })
