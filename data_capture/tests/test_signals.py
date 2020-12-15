from functools import wraps
from unittest.mock import patch
from django.test import TestCase
from django.contrib.auth.models import User, Permission
from django.contrib.admin.models import (
    LogEntry, ADDITION, CHANGE, DELETION
)

from .test_models import ModelTestCase


class MockLogger():
    def __init__(self):
        self.logs = []

    def info(self, fmt, *args):
        self.logs.append(fmt % args)


def mock_logged(fn):
    @wraps(fn)
    @patch('data_capture.signals.logger', MockLogger())
    def wrapper(self):
        import data_capture.signals
        return fn(self, data_capture.signals.logger)

    return wrapper


class PriceListTests(ModelTestCase):
    @mock_logged
    def test_creating_submitted_price_list_logs_message(self, logger):
        self.create_price_list().save()
        self.assertEqual(logger.logs, [
            'Creating SubmittedPriceList for GS-123-4567, submitted by foo.'
        ])

    @mock_logged
    def test_updating_submitted_price_list_does_not_log_message(self, logger):
        pl = self.create_price_list()
        pl.save()
        self.assertEqual(len(logger.logs), 1)
        pl.retire(pl.submitter)
        self.assertEqual(len(logger.logs), 1)


class BaseUserTest(TestCase):
    def setUp(self):
        user = User(username='foo', email='foo@gsa.gov')
        user.save()
        self.user = user


class LogEntryTests(BaseUserTest):
    @mock_logged
    def test_addition_is_logged(self, logger):
        LogEntry(user=self.user, object_repr='blargy',
                 action_flag=ADDITION).save()
        self.assertEqual(logger.logs, ["foo created None 'blargy'"])

    @mock_logged
    def test_deletion_is_logged(self, logger):
        LogEntry(user=self.user, object_repr='blargy',
                 action_flag=DELETION).save()
        self.assertEqual(logger.logs, ["foo deleted None 'blargy'"])

    @mock_logged
    def test_change_is_logged(self, logger):
        LogEntry(user=self.user, object_repr='blargy',
                 action_flag=CHANGE, change_message='oof').save()
        self.assertEqual(logger.logs, ["foo changed None 'blargy': oof"])


class M2MTests(BaseUserTest):
    @mock_logged
    def test_change_is_logged(self, logger):
        perm = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(perm)
        self.assertEqual(logger.logs, [
            "permissions given to user 'foo': "
            "[<Permission: auth | user | Can change user>]"
        ])

    @mock_logged
    def test_remove_is_logged(self, logger):
        perm = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(perm)
        self.user.user_permissions.remove(perm)
        self.assertIn((
            "permissions removed from user 'foo': "
            "[<Permission: auth | user | Can change user>]"
        ), logger.logs)

    @mock_logged
    def test_clear_is_logged(self, logger):
        perm = Permission.objects.get(codename='change_user')
        self.user.user_permissions.add(perm)
        self.user.user_permissions.clear()
        self.assertIn((
            "All permissions removed from user 'foo'"
        ), logger.logs)
