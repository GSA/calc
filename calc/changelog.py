import re
import datetime
import pathlib
from typing import Match
from django.conf import settings
from django.shortcuts import render
from django.utils.safestring import mark_safe
import markdown


CHANGELOG = 'CHANGELOG.md'

PATH = pathlib.Path(__file__).resolve().parent.parent / CHANGELOG

ENCODING = 'utf-8'


class FriendlyRegex:
    '''
    Like a regular expression, but raises a friendly error on
    failure.
    '''

    def __init__(self, name: str, pattern: str) -> None:
        self.name = name
        self.regex = re.compile(pattern, re.MULTILINE)

    def search(self, contents: str, filename=CHANGELOG) -> Match:
        match = self.regex.search(contents)
        if match is None:
            raise ValueError(f"{self.name} not found in {filename}!")
        return match


RELEASE_HEADER_RE = FriendlyRegex(
    'Release header line (e.g. "## 1.2.3 - 2017-01-01")',
    r'^## \[?([0-9.]+)[ \]]?'
)

UNRELEASED_LINK_RE = FriendlyRegex(
    'Unreleased link (e.g. "[unreleased]: http://compare/v1.0.0...HEAD")',
    r'^\[unreleased\]: (.+\.\.\.HEAD)$',
)

UNRELEASED_HEADER = '## [Unreleased][unreleased]'

GH_ISSUE_RE = re.compile(r'(?P<issue_link>#(?P<issue_id>\d+))')
GH_ISSUE_LINK = f'{settings.BASE_GITHUB_URL}/issues/'


def django_view(request):
    contents = strip_preamble(get_contents())
    contents = link_github_issues(contents)
    html = mark_safe(markdown.markdown(contents))  # nosec
    return render(request, 'changelog.html', dict(html=html))


def get_contents():
    '''
    Return the contents of CHANGELOG.md.
    '''

    with PATH.open('r', encoding=ENCODING) as f:
        return f.read()


def link_github_issues(contents):
    '''
    Replaces all matches of GitHub-like issue/PR numbers (starting with '#')
    with Markdown links to issues/PRs in CALC's GitHub repository.

    Examples:

    >>> link_github_issues('abcdef #123 hijklm')
    'abcdef [#123](https://github.com/18F/calc/issues/123) hijklm'

    >>> link_github_issues('abc #12 hij #34') # doctest: +NORMALIZE_WHITESPACE
    'abc [#12](https://github.com/18F/calc/issues/12)
     hij [#34](https://github.com/18F/calc/issues/34)'
    '''
    return GH_ISSUE_RE.sub(
        f'[\g<issue_link>]({GH_ISSUE_LINK}\g<issue_id>)', contents)


def get_unreleased_link(contents):
    '''
    Returns the URL that the "Unreleased" section is hyperlinked to, e.g.:

        >>> get_unreleased_link('[unreleased]: http://compare/v1.0.0...HEAD')
        'http://compare/v1.0.0...HEAD'
    '''

    return UNRELEASED_LINK_RE.search(contents).group(1)


def get_latest_release(contents):
    '''
    Return the latest release of the given changelog, e.g.:

        >>> get_latest_release('## 1.2.3 - 2017-01-01')
        '1.2.3'
    '''

    return RELEASE_HEADER_RE.search(contents).group(1)


def strip_preamble(contents):
    '''
    Removes any expository text before the beginning of the
    "Unreleased" section, if it's non-empty.  If the "Unreleased" section
    is empty, it is removed as well.
    '''

    if get_unreleased_notes(contents).strip():
        result = contents[contents.index(UNRELEASED_HEADER):]
    else:
        result = contents[RELEASE_HEADER_RE.search(contents).start():]
    return result


def bump_version(contents, new_version, date=None):
    '''
    Move the "Unreleased" section of the given changelog to a new release
    with the given version number.

    The new release will be hyperlinked to a GitHub diff between it and the
    previous release, while the "Unreleased" section will be emptied and
    hyperlinked to a GitHub diff between the new release and HEAD.

    Return the contents of the new changelog.
    '''

    if date is None:
        date = datetime.date.today()

    unreleased_diff_link = get_unreleased_link(contents)
    old_version = get_latest_release(contents)
    new_version_header = '## [{}][] - {}'.format(new_version, date)
    new_unreleased_diff_link = unreleased_diff_link.replace(
        'v' + old_version,
        'v' + new_version)
    new_version_diff_link = '[{}]: {}'.format(
        new_version,
        unreleased_diff_link.replace('HEAD', 'v' + new_version))

    contents = contents.replace(
        UNRELEASED_HEADER,
        UNRELEASED_HEADER + '\n\n' + new_version_header)

    contents = contents.replace(
        unreleased_diff_link,
        new_unreleased_diff_link + '\n' + new_version_diff_link)

    return contents


def replace_heading_leaders(contents, char='/'):
    '''
    Replace leading Markdown heading characters ('#') with a different
    character so they're not interpreted as comments in git
    log files (e.g. tag messages).
    '''

    def hashrepl(matchobj):
        return char * len(matchobj.group(0))

    return re.sub(r'^(\#+)', hashrepl, contents, 0, re.MULTILINE)


def get_unreleased_notes(contents):
    '''
    Return the content of the "Unreleased" section of the given changelog.
    '''

    start = contents.index(UNRELEASED_HEADER) + len(UNRELEASED_HEADER) + 1
    end = RELEASE_HEADER_RE.search(contents).start() - 1

    return contents[start:end]
