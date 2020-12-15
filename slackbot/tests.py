from unittest.mock import patch
from django.test import TestCase, override_settings
from click.testing import CliRunner
# import httmock

from . import signals
# from . import bot
from .management.commands import sendtestslack
from data_capture.models import SubmittedPriceList


class SendtestslackTests(TestCase):
    @override_settings(SLACKBOT_WEBHOOK_URL='')
    def test_it_raises_error_when_settings_are_not_defined(self):
        result = CliRunner().invoke(sendtestslack.command)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('SLACKBOT_WEBHOOK_URL must be configured.',
                      result.output)

    @override_settings(SLACKBOT_WEBHOOK_URL='http://boop')
    @patch.object(sendtestslack, 'sendmsg')
    def test_it_has_exit_code_zero_when_sendmsg_is_successful(self, m):
        m.return_value = True
        result = CliRunner().invoke(sendtestslack.command)
        self.assertEqual(result.exit_code, 0)
        self.assertIn('Test Slack message sent successfully!',
                      result.output)
        m.assert_called_with('Hi, this is a test message from '
                             '<http://example.com/|CALC>!')

    @override_settings(SLACKBOT_WEBHOOK_URL='http://boop')
    @patch.object(sendtestslack, 'sendmsg')
    def test_it_raises_error_when_sendmsg_fails(self, m):
        m.return_value = False
        result = CliRunner().invoke(sendtestslack.command)
        self.assertNotEqual(result.exit_code, 0)
        self.assertIn('Sending test Slack message failed.', result.output)


class SignalsTests(TestCase):
    @patch.object(signals, 'sendmsg')
    def test_msg_sent_on_submittedpricelist_creation(self, m):
        instance = SubmittedPriceList()
        instance.id = 5
        instance.status = SubmittedPriceList.STATUS_UNREVIEWED
        signals.on_submittedpricelist_save(
            SubmittedPriceList,
            created=True,
            instance=instance,
        )
        m.assert_called_with(
            'A new <http://example.com/admin/data_capture/'
            'unreviewedpricelist/5/change/|price list> has been submitted!'
        )
