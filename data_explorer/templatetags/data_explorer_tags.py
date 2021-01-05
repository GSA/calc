import re

from django import template
from django.contrib.sites.models import Site
from django.utils.text import normalize_newlines

from calc.site_utils import get_canonical_url

register = template.Library()


@register.inclusion_tag('_head_meta.html', takes_context=True)
def head_meta(context, *args, **kwargs):
    """
    Outputs an array of tags in the head for search engines and social media outlets
    including relevant icon and image meta tags.

    First, it looks in the general context, to see if variables were set in the view.
    In that case, the variables passed straight through from the view to the parent
    template and on through this tag. In this case, the usage would simply be:

    {% head_meta %}

    Note that the variables should be named the same as the arguments below,
    and you must set them in the view. If you don't, it will fall back on the defaults.

    You can also use named arguments:
    {% head_meta title=title %} or
    {% head_meta title="My most excellent page" %}

    Possible arguments are:
    `title`: The title of the page. Should be set in most cases.
    `description`: Used for meta description, OG and twitter tags.
        Defaults to standard site description.
    `meta_image`: The image social services should use to reference the page.
        Pass the full path within the staticfile directory. Defaults to calc_meta_logo.png

    All arguments are optional and sane defaults will be set.
    """
    if 'description' in context:
        description = context['description']
    elif 'description' in kwargs:
        description = kwargs['description']
    else:
        description = """Contract-Awarded Labor Category (CALC) tools let
            federal contracting officers and others find awarded prices
            for negotiations for labor contracts."""
    if 'title' in context:
        title = context['title']
    elif 'title' in kwargs:
        title = kwargs['title']
    else:
        title = "Contract-Awarded Labor Category"
    if 'meta_image' in context:
        meta_image = context['meta_image']
    elif 'meta_image' in kwargs:
        meta_image = kwargs['meta_image']
    else:
        meta_image = 'frontend/images/calc_meta_logo.png'

    return {
        'description': description,
        'title': title,
        'site': Site.objects.get_current(),
        'canonical_url': get_canonical_url(context['request']),
        'meta_image': meta_image
    }


@register.simple_tag
def striptext(text):
    """
    Removes line breaks, leading and trailing spaces,
    and any extraneous spaces, leaving only single spaces.
    """
    text = normalize_newlines(text).replace('\n', '')
    text = text.strip()
    # Using re to remove extraneous spaces
    text = re.sub(' +', ' ', text)
    return text


@register.tag(name="capture")
def do_capturing(parser, token):
    """
    Takes *whatever* is between the opening and closing capture tags
    and casts it to a variable for reuse later in the template.

    Usage:
    {% capture as foo %}
       Whole lotta stuff could be happening here.
    {% endcapture %}
    {{ foo }}

    It also takes an optional 'strip' argument that
    removes newlines and extra spaces from the captured text.
    This can be handy if you want to condense the output
    or remove extra spaces Django puts in.

    Notes:
    You must use capture in the same block you're outputting to.
    You cannot use it across blocks. This is intentional in Django.

    Use this sparingly. Most times this should probably be done in the view.
    """
    nodelist = parser.parse(('endcapture'))
    parser.delete_first_token()
    bits = token.split_contents()

    if len(bits) < 3:
        raise template.TemplateSyntaxError(
            "The 'capture' tag expects you to provide a variable name: {% capture as foo %}"
        )
    # if we passed an additional argument, pass that along
    if len(bits) == 4:
        return CaptureNode(nodelist, bits[2], bits[3])
    # variable name should be the third bit, so...
    return CaptureNode(nodelist, bits[2])


class CaptureNode(template.Node):
    def __init__(self, nodelist, varname, strip=False):
        self.nodelist = nodelist
        self.varname = varname
        self.strip = strip

    def render(self, context):
        output = self.nodelist.render(context)
        if self.strip:
            # use the striptext tag defined above as a funtion
            output = striptext(output)
        context[self.varname] = output
        return ''
