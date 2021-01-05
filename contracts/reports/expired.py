from django.utils import timezone

from contracts.models import Contract
from .base import BaseMetric


class Metric(BaseMetric):
    '''
    Find labor rates whose contracts are expired.
    '''
    def get_queryset(self):
        Contract.objects.filter(contract_end__lt=timezone.now()).delete()
        return Contract.objects.filter(
            contract_end__lt=timezone.now()
        )

    desc = 'labor rates are from expired contracts.'

    verbose_name = 'expired rates'
