from textwrap import indent
from django.core.management.base import BaseCommand

from contracts.reports import BaseMetric, ALL_METRICS


class Command(BaseCommand):
    help = '''
    Generate a report on the quality of CALC's data.
    '''

    def report(self, metric: BaseMetric):
        msg = f"{metric.count()} {metric.desc_text}"
        self.stdout.write(msg)
        self.stdout.write("\n")
        if metric.footnote:
            self.stdout.write(indent(metric.footnote_text, '  '))
            self.stdout.write("\n")

    def handle(self, *args, **kwargs):
        for metric in ALL_METRICS:
            self.report(metric)
