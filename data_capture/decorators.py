from functools import wraps

from django.shortcuts import redirect

from frontend import ajaxform


def handle_cancel(*args, redirect_name='index', key_prefix='data_capture:'):
    '''
    Decorator to handle cancel behavior in Data Capture flows.
    The associated request's POST data is checked for a 'cancel' key,
    and, if found, all session keys that start with `key_prefix`
    are deleted and the request is redirected to `redirect_name`.
    '''

    no_args = False
    if len(args) == 1 and callable(args[0]):
        # We were called without args
        function = args[0]
        no_args = True

    def decorator(function):
        @wraps(function)
        def wrapper(request, *args, **kwargs):
            if request.method == 'POST' and 'cancel' in request.POST:
                if key_prefix:
                    # .keys() returns an iterator, which can't be deleted from
                    # while in a loop, so we use list() to get an actual list
                    session_keys = list(request.session.keys())
                    for k in session_keys:
                        if k.startswith(key_prefix):
                            del request.session[k]

                # if AJAX request, then send JSON response
                # that has a 'redirect_url' property
                if request.is_ajax():
                    return ajaxform.ajax_redirect(redirect_name)

                # redirect to the view named redirect_name
                return redirect(redirect_name)

            else:
                # pass through
                return function(request, *args, **kwargs)

        return wrapper

    if no_args:
        return decorator(function)
    else:
        return decorator
