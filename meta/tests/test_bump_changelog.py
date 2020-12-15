from unittest import TestCase
from unittest.mock import patch
from pathlib import Path
from click.testing import CliRunner

from ..management.commands import bump_changelog
from calc import changelog
from calc.tests.test_changelog import UtilTests


def patch_new_version(version):
    return patch.object(bump_changelog, '__version__', version)


def patch_changelog_contents(contents):
    return patch.object(changelog, 'get_contents', lambda: contents)


class BumpChangelogTests(TestCase):
    @patch_new_version('9.0.0')
    @patch_changelog_contents(UtilTests.AFTER_BUMP)
    def test_it_reports_error_on_no_release_notes(self):
        result = CliRunner().invoke(bump_changelog.command)
        self.assertIn('The new release has no release notes', result.output)
        self.assertNotEqual(result.exit_code, 0)

    @patch_new_version('0.0.1')
    @patch_changelog_contents(UtilTests.BEFORE_BUMP)
    def test_it_reports_error_if_new_version_is_invalid(self):
        result = CliRunner().invoke(bump_changelog.command)
        self.assertIn('Please change calc/version.py', result.output)
        self.assertNotEqual(result.exit_code, 0)

    @patch_new_version('9.0.0')
    @patch_changelog_contents(UtilTests.BEFORE_BUMP)
    def test_it_works(self):
        runner = CliRunner()

        with runner.isolated_filesystem():
            fakelog = Path('fake-changelog.md')
            with patch.object(changelog, 'PATH', fakelog):
                result = CliRunner().invoke(bump_changelog.command)

                self.assertIn('Modifying CHANGELOG.md', result.output)
                self.assertEqual(result.exit_code, 0)

                with fakelog.open('r', encoding=changelog.ENCODING) as f:
                    self.assertIn('9.0.0', f.read())

                tagmsg = Path('tag-message-v9.0.0.txt')

                with tagmsg.open('r', encoding=changelog.ENCODING) as f:
                    self.assertIn('Fixed some stuff', f.read())


del UtilTests  # So our test runner doesn't find and run them.
