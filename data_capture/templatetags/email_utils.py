from django import template
from django.contrib.staticfiles.storage import staticfiles_storage

from calc.site_utils import absolutify_url


register = template.Library()


@register.simple_tag()
def absolute_static(url):
    '''
    This is like the {% static %} template tag, but it ensures that
    the returned URL is absolute, so that it can be included in an
    email.

    Unlike the {% static %} tag, however, it doesn't allow the URL
    to be assigned to a context variable.
    '''

    return absolutify_url(staticfiles_storage.url(url))


@register.simple_tag(takes_context=True)
def cta(context, url, action_text):
    '''
    A call-to-action. This shows up as a button for HTML emails;
    for plaintext emails, it shows up like this:

        >>> cta({}, 'http://boop', 'Do something cool')
        'To do something cool, visit http://boop.'
    '''

    if not context.get('is_html_email'):
        action_text = action_text[0].lower() + action_text[1:]
        return f"To {action_text}, visit {url}."

    t = context.template.engine.get_template('email/cta.html')

    return t.render(template.Context({
        'url': url,
        'action_text': action_text,
    }))
