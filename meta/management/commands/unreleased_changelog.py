import djclick as click

from calc import changelog


@click.command()
def command():
    '''
    Print the "Unreleased" section of CHANGELOG.md to stdout.
    '''

    notes = changelog.get_unreleased_notes(changelog.get_contents())
    click.echo(notes.strip())
