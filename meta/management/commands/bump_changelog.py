import djclick as click
from semantic_version import Version
from django.core.management.base import CommandError

from calc.version import __version__
from calc import changelog


@click.command()
def command():
    '''
    Updates CHANGELOG.md to reflect the new version specified in
    calc/version.py.

    The "Unreleased" section of the changelog will be moved to a
    new release with the given version number.

    The new release will be hyperlinked to a GitHub diff between it and the
    previous release, while the "Unreleased" section will be emptied and
    hyperlinked to a GitHub diff between the new release and HEAD.
    '''

    markdown = changelog.get_contents()
    new_version = Version(__version__)
    old_version = Version(changelog.get_latest_release(markdown))
    base_release_notes = changelog.get_unreleased_notes(markdown).strip()
    release_notes = 'Release ' + str(new_version) + '\n\n' + \
        changelog.replace_heading_leaders(base_release_notes)
    release_notes_filename = 'tag-message-v%s.txt' % new_version

    if new_version <= old_version:
        raise CommandError(
            'Please change calc/version.py to reflect the new '
            'version you\'d like to bump CHANGELOG.md to.')

    if base_release_notes == '':
        raise CommandError(
            'The new release has no release notes! Please add some '
            'under the "Unreleased" section of CHANGELOG.md.')

    click.echo('Modifying CHANGELOG.md to reflect new '
               'release %s.' % new_version)

    new_markdown = changelog.bump_version(markdown, str(new_version))

    with changelog.PATH.open('w', encoding=changelog.ENCODING) as f:
        f.write(new_markdown)

    click.echo('Writing release notes to %s.' % release_notes_filename)

    with open(release_notes_filename, 'w', encoding=changelog.ENCODING) as f:
        f.write(release_notes + '\n')

    click.echo('Done. To undo these changes, run '
               '"git checkout -- CHANGELOG.md".')
