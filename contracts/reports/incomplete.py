from contracts.models import Contract
from .base import BaseMetric


class Metric(BaseMetric):
    '''
    Find labor rates that are missing key data.
    '''

    def get_queryset(self):
        return Contract.objects.filter(
            education_level=None,
        )

    desc = 'labor rates have missing data.'

    footnote = '''
    By "missing key data", we currently mean rates that
    have no minimum education level.
    '''

    verbose_name = 'incomplete rates'
