from datetime import datetime  # noqa (needed for doctest)
from django import template
from django.utils.formats import date_format, time_format
from pytz import timezone

register = template.Library()


@register.filter
def tz_timestamp(value, tz_name="US/Eastern"):
    '''
    This template filter formats the given timezone-aware datetime into
    a more readable format, localized to the timezone specified by tz_name.

    >>> tz_timestamp(datetime(2016, 2, 11, 14, 30, 5))
    'Feb. 11, 2016 at 9:30 a.m. (EST)'
    '''
    try:
        tz = timezone(tz_name)
        ts = value.astimezone(tz)
        return f"{date_format(ts)} at {time_format(ts)} ({ts.tzname()})"
    except (AttributeError, ValueError):
        # just return the original value
        return value
