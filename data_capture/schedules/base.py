'''
This module contains BasePriceList, the abstract base class for
price lists being imported into CALC.

Different schedules will need different kinds of business logic for
parsing their particular kinds of price lists and adding them to CALC;
BasePriceList contains a variety of extension points to accommodate
for these specifics while providing a common interface to clients.
'''

import re
import abc
from typing import Dict, Any, Optional, List

from django.template.loader import render_to_string
from django.core.validators import (
    MinValueValidator, RegexValidator)
from django.http import HttpRequest
from django.utils.safestring import SafeString, mark_safe
from django.forms import Form
from django.core.files.uploadedfile import UploadedFile

from contracts.loaders.region_10 import FEDERAL_MIN_CONTRACT_RATE
from ..models import SubmittedPriceList


min_price_validator = MinValueValidator(
    FEDERAL_MIN_CONTRACT_RATE,
    message='Price must be at least the federal contractor minimum wage '
            '(${0:.2f})'.format(FEDERAL_MIN_CONTRACT_RATE))


hour_regex = re.compile(r'^hour(ly|s)?$', flags=re.IGNORECASE)

hourly_rates_only_validator = RegexValidator(
    hour_regex, 'Value must be "Hour" or "Hourly"')


class ConcreteBasePriceListMethods:
    '''
    Concrete methods for all price lists being imported into CALC.

    We're separating these from the abstract methods so they can
    be easily tested on their own.
    '''

    # Path to the template used for presenting an example of
    # what to upload.
    upload_example_template: Optional[str] = None

    # This is a list of Django Form objects representing
    # valid rows in the price list.
    valid_rows: List[Form]

    # This is a list of Django Form objects representing
    # invalid rows in the price list.
    invalid_rows: List[Form]

    def __init__(self) -> None:
        self.valid_rows = []
        self.invalid_rows = []

    def is_empty(self) -> bool:
        '''
        Returns whether the price list contains no data.
        '''

        return not (self.valid_rows or self.invalid_rows)

    @classmethod
    def get_upload_example_context(cls) -> Optional[Dict[str, Any]]:
        '''
        Returns a dictionary to use as the context for the upload example
        template.
        '''

        return None

    @classmethod
    def render_upload_example(cls, request: HttpRequest=None) -> SafeString:
        '''
        Returns the HTML containing an example of what the schedule
        expects the user to upload, along with any other pertinent
        information.

        If the schedule has no example, returns an empty string.
        '''

        if cls.upload_example_template is not None:
            return render_to_string(cls.upload_example_template,
                                    cls.get_upload_example_context(),
                                    request=request)
        return mark_safe('')  # nosec


class BasePriceList(ConcreteBasePriceListMethods, metaclass=abc.ABCMeta):
    '''
    Abstract base class for price lists being imported into CALC.
    '''

    # Human-readable name of the schedule to which the price list
    # belongs. Subclasses should override this.
    title = 'Unknown Schedule'

    # Extra instructions text to use for the upload widget.
    upload_widget_extra_instructions: Optional[str] = None

    @abc.abstractmethod
    def add_to_price_list(self, price_list: SubmittedPriceList) -> None:
        '''
        Adds the price list's valid rows to the given
        data_capture.models.SubmittedPriceList model.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def serialize(self) -> Any:
        '''
        Returns a JSON-serializable representation of the
        price list.
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def to_table(self) -> SafeString:
        '''
        Returns a string of the HTML table representation of the valid rows
        of the price list
        '''

        raise NotImplementedError()

    @abc.abstractmethod
    def to_error_table(self) -> SafeString:
        '''
        Returns a string of the HTML table representation of the invalid
        rows of the price list
        '''

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def deserialize(cls, obj: Any) -> 'BasePriceList':
        '''
        Given an object previously returned by serialize(),
        Return a BasePriceList subclass.
        '''

        raise NotImplementedError()

    @classmethod
    @abc.abstractmethod
    def load_from_upload(cls, f: UploadedFile) -> 'BasePriceList':
        '''
        Given an UploadedFile, return a BasePriceList
        subclass that represents the price list. If the file could not
        be read, raise a ValidationError.

        For more details on UploadedFile, see:

            https://docs.djangoproject.com/en/1.9/ref/files/uploads/
        '''

        raise NotImplementedError()
