'''
    This module provides back-end Django utilities that make it
    easier to interact with the front-end ajaxform component.

    This module is tightly coupled to ajaxform.js.
'''

#from django.core.urlresolvers import reverse
from django.urls import reverse
from django.http import JsonResponse, HttpResponse, HttpResponseRedirect
from django.template.loader import render_to_string


def ajax_redirect(viewname, **kwargs):
    '''
    Given a viewname returns a JSON response containing an
    object with key called 'redirect_url' used by ajaxform.js
    to redirect the client browser.
    '''
    return JsonResponse({'redirect_url': reverse(viewname, kwargs=kwargs)})


def redirect(request, viewname, **kwargs):
    '''
    Redirect the request to the given URL pattern name or the callable
    view object.

    This can be called from a form-based view that handles both
    ajaxform-intiated ajax requests *and* browser-initiated requests.
    The function will detect which client initiated the request and
    act accordingly.
    '''
    if request.is_ajax():
        return ajax_redirect(viewname, **kwargs)

    return HttpResponseRedirect(reverse(viewname, kwargs=kwargs))


def render(request, context, template_name, ajax_template_name):
    '''
    Render a template response to the client, choosing a
    different template depending on whether the request was
    initiated by ajaxform or a browser.

    Typically this is used within a form-based view; `ajax_template_name`
    is usually a partial containing only the form, while
    `template_name` is a full page containing the form.

    Regardless of which template is used, the same context is passed
    into it.
    '''

    if request.is_ajax():
        return JsonResponse({
            'form_html': render_to_string(ajax_template_name, context,
                                          request=request)
        })

    return HttpResponse(render_to_string(template_name, context,
                                         request=request))
