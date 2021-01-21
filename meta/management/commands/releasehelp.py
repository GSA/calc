import pathlib
import djclick as click
import markdown

MY_DIR = pathlib.Path(__file__).resolve().parent

ROOT_DIR = MY_DIR.parent.parent.parent

RELEASE_MD = ROOT_DIR / 'docs' / 'release.rst'

HTML_TEMPLATE = '''\
<!DOCTYPE html>
<meta charset="utf-8">
<style>
body {
  max-width: 640px;
  margin: 0 auto;
  font-family: Georgia, serif;
  padding: 0 1em;
}

h1, h2, h3, h4, h5 {
  font-weight: normal;
}

code {
  white-space: pre;
}
</style>
<title>How to release v%(version)s</title>
%(html)s
'''


@click.command()
@click.option('-r', '--version-to-release', prompt=True,
              help='New version number to release')
def command(version_to_release):
    '''
    Creates instructions for releasing a specific version of CALC.
    '''

    v = version_to_release

    with RELEASE_MD.open('r', encoding='utf-8') as f:
        md = f.read()

    md = md.replace('0.0.4', v)

    basename = 'release-v%s-instructions' % v
    markdown_filename = '%s.txt' % basename
    html_filename = '%s.html' % basename

    with pathlib.Path(markdown_filename).open('w', encoding='utf-8') as f:
        f.write(md)

    with pathlib.Path(html_filename).open('w', encoding='utf-8') as f:
        f.write(HTML_TEMPLATE % dict(
            version=v,
            html=markdown.markdown(md)
        ))

    click.echo('Wrote plaintext instructions to %s.' % markdown_filename)
    click.echo('Wrote HTML instructions to %s.' % html_filename)
    click.echo('Please open one of these to learn how release v%s.' % v)
