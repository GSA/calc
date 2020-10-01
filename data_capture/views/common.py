import urllib.parse
from django.contrib import messages
from django.template.defaultfilters import pluralize
# from django.core.urlresolvers import reverse
from django.urls import reverse

from ..schedules import registry


def add_generic_form_error(request, form):
    messages.add_message(
        request, messages.ERROR,
        'Oops! Please correct the following error{}.'
            .format(pluralize(form.errors))
    )


def add_change_success_message(request):
    messages.add_message(
        request,
        messages.SUCCESS,
        "Your changes have been submitted. An administrator will "
        "review them before they are live in CALC."
    )


def build_url(viewname, reverse_kwargs=None, **kwargs):
    '''
    Build a URL using the given view name and the given query string
    arguments, returning the result:

        >>> build_url('data_capture:step_4', a='1')
        '/data-capture/step/4?a=1'

    Any keyword arguments that are `None` will be excluded, though:

        >>> build_url('data_capture:step_4', a=None)
        '/data-capture/step/4'

    Any value to the  `reverse_kwargs` argument will be passed through as the
    `kwargs` argument to `reverse`. This is useful for setting url parameters.

        >>> build_url('data_capture:price_list_details',
        ...           reverse_kwargs={'id': 5})
        '/data-capture/price-lists/5'
    '''

    url = reverse(viewname, kwargs=reverse_kwargs)
    query = [
        (key, kwargs[key]) for key in kwargs
        if kwargs[key] is not None
    ]
    if not query:
        return url
    return '{}?{}'.format(url, urllib.parse.urlencode(query))


def get_nested_item(obj, keys, default=None):
    '''
    Get a nested item from a nested structure of dictionary-like objects,
    returning a default value if any expected keys are not present.

    Examples:

        >>> d = {'foo': {'bar': 'baz'}}
        >>> get_nested_item(d, ('foo', 'bar'))
        'baz'
        >>> get_nested_item(d, ('foo', 'blarg'))
    '''

    key = keys[0]
    if key not in obj:
        return default
    if len(keys) > 1:
        return get_nested_item(obj[key], keys[1:], default)
    return obj[key]


def get_deserialized_gleaned_data(
        request, primary_session_key='data_capture:price_list'):
    '''
    Gets 'gleaned_data' from session and uses the registry to deserialize
    it. Returns None if 'gleaned_data' is not in session.
    '''
    serialized_gleaned_data = get_nested_item(request.session, (
        primary_session_key, 'gleaned_data'))
    if serialized_gleaned_data:
        return registry.deserialize(serialized_gleaned_data)
    return None
