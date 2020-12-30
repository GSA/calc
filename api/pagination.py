from collections import OrderedDict
from rest_framework import pagination
from rest_framework.response import Response
from django.conf import settings


class ContractPagination(pagination.PageNumberPagination):

    def __init__(self, context=None):
        super().__init__()
        if context is None:
            context = {}
        self.context = context
        self.page_size = settings.PAGINATION

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('average', self.get_average()),
            ('minimum', self.get_minimum()),
            ('maximum', self.get_maximum()),
            ('wage_histogram', self.get_wage_histogram()),
            ('first_standard_deviation', self.get_first_standard_deviation()),
            ('results', data)
        ]))

    def get_average(self):
        return self.context.get('average', 0)

    def get_minimum(self):
        return self.context.get('minimum', 0)

    def get_maximum(self):
        return self.context.get('maximum', 0)

    def get_wage_histogram(self):
        return self.context.get('wage_histogram', [])

    def get_first_standard_deviation(self):
        return self.context.get('first_standard_deviation', 0)
