from unittest import TestCase
from pathlib import Path
from click.testing import CliRunner

from ..management.commands import releasehelp


class ReleaseHelpTests(TestCase):
    def test_it_generates_text_and_html_files(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            result = runner.invoke(releasehelp.command, ['-r', '1.9.9'])

            self.assertEqual(result.exit_code, 0)

            basename = 'release-v1.9.9-instructions'

            with Path(basename + '.txt').open('r', encoding='utf-8') as f:
                self.assertIn('1.9.9', f.read())

            with Path(basename + '.html').open('r', encoding='utf-8') as f:
                html = f.read()
                self.assertIn('<!DOCTYPE html>', html)
                self.assertIn('1.9.9', html)
