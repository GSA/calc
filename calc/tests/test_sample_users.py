from django.test import override_settings, TestCase, SimpleTestCase
from django.http import Http404
from django.core.management import call_command

from .. import sample_users


class NotFoundTests(SimpleTestCase):
    @override_settings(DEBUG=False, HIDE_DEBUG_UI=False)
    def test_when_not_in_debug(self):
        with self.assertRaisesMessage(Http404, sample_users.DEBUG_ONLY_MSG):
            sample_users.login_sample_user(None, None)

    @override_settings(DEBUG=True, HIDE_DEBUG_UI=True)
    def test_when_hiding_debug_ui(self):
        with self.assertRaisesMessage(Http404, sample_users.DEBUG_ONLY_MSG):
            sample_users.login_sample_user(None, None)

    @override_settings(DEBUG=True, HIDE_DEBUG_UI=False)
    def test_when_sample_user_not_found(self):
        with self.assertRaisesMessage(Http404, 'Sample user not found!'):
            sample_users.login_sample_user(None, 'blarg')


@override_settings(DEBUG=True, HIDE_DEBUG_UI=False)
class SampleUsersTests(TestCase):
    username = sample_users.SAMPLE_USERS[0].username

    def setUp(self):
        call_command('initgroups')

    def test_all_sample_users_are_valid(self):
        for su in sample_users.SAMPLE_USERS:
            user = sample_users.get_or_create_sample_user(su.username)
            self.assertEqual(user.email, su.email)
            self.assertEqual(user.is_staff, su.is_staff)
            self.assertEqual(user.is_superuser, su.is_superuser)
            self.assertEqual([g.name for g in user.groups.all()], su.groups)

    def test_getting_sample_user_twice_returns_original(self):
        user1 = sample_users.get_or_create_sample_user(self.username)
        user2 = sample_users.get_or_create_sample_user(self.username)
        self.assertEqual(user1.pk, user2.pk)

    def test_view_logs_in_and_redirects(self):
        res = self.client.get(f'/login-sample-user/{self.username}?next=/boop/')
        self.assertEqual(res.status_code, 302)
        self.assertEqual(res['location'], '/boop/')
        user = sample_users.get_or_create_sample_user(self.username)
        self.assertEqual(self.client.session['_auth_user_id'], str(user.pk))
