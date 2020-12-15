import re
from pathlib import Path
from typing import Optional
from django.utils.safestring import SafeString
from django.shortcuts import render
from django.urls import reverse
from django.http import Http404


MY_DIR = Path(__file__).parent.resolve()

EXAMPLES_DIRNAME = 'styleguide_fullpage_examples'

EXAMPLES_DIR = MY_DIR / 'templates' / EXAMPLES_DIRNAME

# We need to be careful to make this regular expression for
# example names very restrictive, because we use the name
# as part of file paths; so we don't e.g. want to allow
# periods or dashes.
REGEX = r'([0-9A-Za-z_\-]+)'

# Code in full-page examples between BEGIN_SNIPPET and END_SNIPPET
# will be treated as the HTML source of the example, for display
# in the style guide. If they're not found in the example, then
# the entire contents of the example will be used.
BEGIN_SNIPPET = r'{# BEGIN SNIPPET #}'

END_SNIPPET = r'{# END SNIPPET #}'

SNIPPET_RE = re.compile(
    r'.*' + BEGIN_SNIPPET + r'\n(.*)' + END_SNIPPET + r'.*',
    re.MULTILINE | re.DOTALL)


def to_path(name: str) -> Path:
    return EXAMPLES_DIR / f'{name}.html'


def _get_snippet(text: str) -> Optional[str]:
    match = SNIPPET_RE.match(text)
    return match.group(1) if match else None


def get_html_source(name: str) -> SafeString:
    text = to_path(name).read_text()
    return SafeString(_get_snippet(text) or text)


def get_url(name: str) -> str:
    return reverse('styleguide:fullpage_example', args=(name,))


def exists(name: str) -> bool:
    return to_path(name).exists()


def view(request, name: str):
    if not exists(name):
        raise Http404("fullpage example does not exist")
    return render(request, f'{EXAMPLES_DIRNAME}/{name}.html')
