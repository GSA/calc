from unittest import TestCase
from click.testing import CliRunner

from ..management.commands import unreleased_changelog


class UnreleasedChangelogTests(TestCase):
    def test_it_does_not_explode(self):
        result = CliRunner().invoke(unreleased_changelog.command)
        self.assertEqual(result.exit_code, 0)
