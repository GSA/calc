import os.path
from html.parser import HTMLParser
from textwrap import dedent
from inspect import getsourcefile
from importlib import import_module
from pathlib import Path

from django import template
from django.conf import settings
from django.utils.safestring import SafeString
from django.utils.module_loading import import_string
from django.utils.html import escape
from django.utils.text import slugify
from django.template.backends.django import get_installed_libraries
from django.template import Engine

from styleguide import fullpage_example as _fullpage_example


DEFAULT_GITHUB_BRANCH = 'develop'

MY_DIR = os.path.abspath(os.path.dirname(__file__))

ROOT_DIR = os.path.normpath(os.path.join(MY_DIR, '..', '..'))

SCSS_DIR = 'frontend/source/sass'

JS_DIR = 'frontend/source/js'

register = template.Library()


@register.tag
def template_example(parser, token):
    '''
    Render both the original source code and the rendered output
    of the Django template code between this tag and
    its corresponding {% endtemplate_example %}.
    '''

    first_token = parser.tokens[0]
    nodelist = parser.parse(('endtemplate_example',))
    last_token = parser.tokens[0]
    parser.delete_first_token()
    contents = parser.origin.loader.get_contents(parser.origin)
    lines = contents.splitlines()
    text = '\n'.join(lines[first_token.lineno:last_token.lineno - 1])
    return TemplateExampleNode(text, nodelist)


class TemplateExampleNode(template.Node):
    def __init__(self, template_source, nodelist):
        self.template_source = template_source
        self.nodelist = nodelist

    def render(self, context):
        t = context.template.engine.get_template('styleguide_template_example.html')

        return t.render(template.Context({
            'template_rendering': self.nodelist.render(context),
            'template_source': self.template_source,
        }))


@register.tag
def guide(parser, token):
    '''
    A {% guide %} represents an HTML document composed into sections with a
    table of contents linking to them.
    '''

    nodelist = parser.parse(('endguide',))
    parser.delete_first_token()
    return GuideNode(nodelist)


class GuideNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        context['_sections'] = []

        html = self.nodelist.render(context)

        t = context.template.engine.get_template('styleguide_with_toc.html')

        result = t.render(template.Context({
            'html': html,
            'sections': context['_sections']
        }))

        del context['_sections']

        return result


def github_url_for_path(path):
    '''
    Given a relative path from the root of the repository, returns a
    GitHub URL to its syntax-highlighted source code.
    '''

    return '{}/tree/{}/{}'.format(
        settings.BASE_GITHUB_URL,
        DEFAULT_GITHUB_BRANCH,
        path
    )


class WebComponentHTMLParser(HTMLParser):
    def handle_starttag(self, tag, attrs):
        self.tag = tag
        self.extends = ''
        for attr, val in attrs:
            if attr == 'is':
                self.extends = val


def get_template_tag_library_and_url(name):
    '''
    Return a tuple containing the Python module for the given template tag
    library, and the GitHub URL to its source code.
    '''

    libs = get_installed_libraries()

    if name not in libs:
        raise ValueError(f'template tag library {name} not found')

    mod = import_module(libs[name])

    if not mod.__file__.startswith(ROOT_DIR):
        raise ValueError(f'template tag library {name} is not in project')

    url = github_url_for_path(os.path.relpath(mod.__file__, ROOT_DIR))

    return mod, url


@register.simple_tag
def template_tag(library, tag):
    '''
    Render the name of a template tag from the given template tag library,
    hyperlinked to its source code.
    '''

    mod, url = get_template_tag_library_and_url(library)
    func = mod.register.tags[tag]
    while hasattr(func, '__wrapped__'):
        func = func.__wrapped__
    lineno = func.__code__.co_firstlineno

    return SafeString(
        f'<code><a href="{url}#L{lineno}">{{%&nbsp;{tag}&nbsp;%}}</a></code>'
    )


@register.simple_tag
def template_tag_library(name):
    '''
    Render the name of a template tag library that is hyperlinked
    to its source code.
    '''

    mod, url = get_template_tag_library_and_url(name)

    return SafeString(f'<code><a href="{url}">{name}</a></code>')


def get_template_path(template_name: str) -> Path:
    '''
    Given a Django template path, return an absolute path to it.
    '''

    # Note that we can't simply use the `origin` property of a Template
    # object, because, at least in Django 1.8, it seems this property
    # is None if TEMPLATE_DEBUG is disabled (and we want to be able to
    # render the styleguide in non-debug instances).

    candidates = []

    for loader in Engine.get_default().template_loaders:
        for candidate in loader.get_template_sources(template_name):
            candidates.append(candidate)

    path = None

    for candidate in candidates:
            if os.path.exists(candidate.name):
                path = candidate.name
                break

    if path is None:
        raise ValueError(f'Template {template_name} not found')

    return Path(path)


@register.simple_tag(takes_context=True)
def template_url(context, template_name):
    '''
    Return a GitHub URL to the source of the given template.
    '''

    path = get_template_path(template_name)
    return github_url_for_path(path.relative_to(ROOT_DIR))


@register.simple_tag(takes_context=True)
def template_link(context, template_name):
    '''
    Return a link to the source code of the given template.
    '''

    url = template_url(context, template_name)
    return SafeString(f'<code><a href="{url}">{template_name}</a></code>')


@register.simple_tag
def scss(path):
    '''
    Link to a .scss (SASS) file relative to the base SASS directory.
    '''

    abspath = os.path.join(ROOT_DIR, SCSS_DIR, path)

    if not os.path.exists(abspath):
        raise ValueError(f'{abspath} does not exist')

    url = github_url_for_path(os.path.join(SCSS_DIR, path))

    return SafeString(f'<code><a href="{url}">{path}</a></code>')


@register.simple_tag
def js(path):
    '''
    Link to a JavaScript file relative to the base JS directory.
    '''

    abspath = os.path.join(ROOT_DIR, JS_DIR, path)

    if not os.path.exists(abspath):
        raise ValueError(f'{abspath} does not exist')

    url = github_url_for_path(os.path.join(JS_DIR, path))

    return SafeString(f'<code><a href="{url}">{path}</a></code>')


@register.simple_tag
def webcomponent(html):
    '''
    Link to the source code of a web component, e.g. <foo> or
    <input is="bar">.

    This actually renders markup that client-side code will resolve into
    a definitive link via introspecting the JS runtime environment. The
    front-end will raise an error if the web component or its source code
    can't be found, to help prevent documentation rot.
    '''

    parser = WebComponentHTMLParser()
    parser.feed(html)
    return SafeString(
        '<code><a is="web-component-link" href="{}" '
        'data-tag="{}" data-extends="{}">{}</a></code>'.format(
            escape(github_url_for_path('')),
            escape(parser.tag),
            escape(parser.extends),
            escape(html)
        )
    )


@register.simple_tag
def pyobjname(name):
    '''
    Outputs a link to the source code of the given Python object (e.g.
    module, function, class, etc).

    If the object can't be found, raises an exception. This is primarily
    done to prevent documentation rot.
    '''

    obj = import_string(name)
    filename = os.path.relpath(getsourcefile(obj), ROOT_DIR)

    return SafeString('<code><a href="{}">{}</a></code>'.format(
        escape(github_url_for_path(filename)),
        escape(name)
    ))


@register.simple_tag
def pathname(name):
    '''
    Outputs a link to the source code of the given project-relative path.

    If the path doesn't exist, raises an exception. This is primarily
    done to prevent documentation rot.
    '''

    if not os.path.exists(os.path.join(ROOT_DIR, name)):
        raise Exception('Path %s does not exist' % name)

    return SafeString('<code><a href="{}">{}</a></code>'.format(
        escape(github_url_for_path(name)),
        escape(name)
    ))


@register.simple_tag(takes_context=True)
def fullpage_example(context, name, show_html=True):
    num_key = f'_fullpage_example_{name}'
    num = context.get(num_key, 0) + 1
    context[num_key] = num
    num_str = "" if num == 1 else f"#{num}"

    t = context.template.engine.get_template(
        'styleguide_fullpage_example_iframe.html')
    url = _fullpage_example.get_url(name)
    title = f"Example for {name}{num_str}"
    if show_html:
        html = _fullpage_example.get_html_source(name)
    else:
        html = ''
    return t.render(template.Context({
        'url': url,
        'html': html,
        'title': title,
        'show_html': show_html,
    }))


@register.simple_tag(takes_context=True)
def guide_section(context, name):
    '''
    A section in a guide. It must be used within a {% guide %} tag.
    '''

    if '_sections' not in context:
        raise Exception(r'{% guide_section %} tags should only be used '
                        r'within {% guide%} tags!')
    section = Section(name)
    context['_sections'].append(section)
    t = context.template.engine.get_template('styleguide_section.html')

    return t.render(template.Context({'section': section}))


class Section:

    def __init__(self, name):
        self.name = name
        self.id = slugify(name)


@register.tag
def example(parser, token):
    '''
    An HTML code snippet example in a style guide. Includes both the
    rendered version of the example and the source code.
    '''

    nodelist = parser.parse(('endexample',))
    parser.delete_first_token()
    return ExampleNode(nodelist)


class ExampleNode(template.Node):

    def __init__(self, nodelist):
        self.nodelist = nodelist

    def render(self, context):
        html = SafeString(dedent(self.nodelist.render(context)).strip())

        t = context.template.engine.get_template('styleguide_example.html')

        return t.render(template.Context({'html': html}))
