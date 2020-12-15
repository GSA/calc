'''
This module manages the registration of different types of schedules whose
price lists can be uploaded to CALC.

Registering a schedule in CALC is a bit similar to adding an app to Django.
Every schedule has a class that inherits from BasePriceList, and
settings.DATA_CAPTURE_SCHEDULES refers to a list of strings that correspond
to BasePriceList classes.

Once a schedule is registered, it will appear as an option when a user
chooses to upload a price list to CALC.
'''

from typing import Any, List, Dict, Iterator, NamedTuple, Type, Optional, Tuple

from django.conf import settings
from django.forms import ValidationError
from django.core.files.uploadedfile import UploadedFile
from django.utils.module_loading import import_string

from data_capture.schedules.base import BasePriceList


class Choice(NamedTuple):
    '''
    Represents a schedule choice for a price list upload.
    '''

    # The fully-qualified BasePriceList subclass name that
    # encapsulates the schedule's business logic, e.g.
    # "foo.bar.Schedule2PriceList".
    classname: str

    # The human-readable name of the schedule, e.g. "Schedule 2".
    title: str


# Global list of all schedule choices.
CHOICES: List[Choice] = []

# Global dictionary that maps fully-qualified class names to
# their class instances.
CLASSES: Dict[str, Type[BasePriceList]] = {}


def _classname(cls: type) -> str:
    '''Return the fully-qualified class name for a class.'''

    return '%s.%s' % (cls.__module__, cls.__name__)


def populate_from_settings():
    '''
    Populate the registry by loading from the list
    of class names in Django's settings.DATA_CAPTURE_SCHEDULES.
    '''

    global CHOICES, CLASSES

    CHOICES = []
    CLASSES = {}

    for classname in settings.DATA_CAPTURE_SCHEDULES:
        cls = import_string(classname)
        CHOICES.append(Choice(classname, cls.title))
        CLASSES[classname] = cls


def get_choices() -> Iterator[Choice]:
    '''
    Return an iterator of all the schedules whose price lists can be uploaded.
    '''

    for choice in CHOICES:
        yield choice


def get_class(classname: str) -> Type[BasePriceList]:
    '''
    Given a fully-qualified BasePriceList subclass name that is registered,
    return the subclass. Raises a KeyError if the subclass isn't
    registered.
    '''

    return CLASSES[classname]


def get_classname(instance: BasePriceList) -> str:
    '''
    Given a BasePriceList instance, returns its fully-qualified class
    name.

    If its class name isn't registered, raises a KeyError.
    '''

    classname = _classname(instance.__class__)
    if classname not in CLASSES:
        raise KeyError(classname)
    return classname


def load_from_upload(classname: str, f: UploadedFile) -> BasePriceList:
    '''
    Loads the given uploaded price list using the given registered
    price list class.
    '''

    return CLASSES[classname].load_from_upload(f)


def smart_load_from_upload(classname: str, f: UploadedFile) -> BasePriceList:
    '''
    Attempt to intelligently load the given Django UploadedFile,
    interpreting it as a price list for the given schedule class name.

    If interpreting it under the preferred schedule results in either
    a ValidationError or no valid rows, attempts will be made to
    re-interpret the file under different schedules. The first found
    that yields better interpretations of the data will be returned.

    If no better matches are found, the original result or exception
    (from interpreting the data under the preferred price list) will
    be returned.
    '''

    original_error = None
    pricelist: Optional[BasePriceList] = None

    try:
        pricelist = load_from_upload(classname, f)
    except ValidationError as e:
        original_error = e

    if original_error or (pricelist and not pricelist.valid_rows):
        # See if any of our other registered schedules can make better sense
        # of it.
        next_best_pricelist = None
        for fallback, _ in CHOICES:
            if fallback == classname:
                continue
            try:
                f.seek(0)
                next_best_pricelist = load_from_upload(fallback, f)
                if next_best_pricelist.valid_rows:
                    pricelist = next_best_pricelist
                    break
            except ValidationError as e:
                pass

    if pricelist is None:
        default_error = ValidationError('Unrecognized price list!')
        raise original_error or default_error

    return pricelist


# A serialized price list is a tuple comprised of its fully-qualified
# class name and its class-specific serialization data.
#
# This allows us to easily "route" a price list's serialized
# representation to its class-specific deserializer.
SerializedPriceList = Tuple[str, Any]


def serialize(pricelist: BasePriceList) -> SerializedPriceList:
    '''
    Given a BasePriceList, returns its serialization.

    Raises a KeyError if the BasePriceList's class is not
    registered.
    '''

    classname = _classname(pricelist.__class__)

    if classname not in CLASSES:
        raise KeyError(classname)

    return (classname, pricelist.serialize())


def deserialize(data: SerializedPriceList) -> BasePriceList:
    '''
    Given a serialized price list, deserializes it, returning
    its BasePriceList representation.
    '''

    classname, d = data

    return CLASSES[classname].deserialize(d)


populate_from_settings()
