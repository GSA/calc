from django.test import TestCase
from django.contrib.auth.models import User, Group

from ..management.commands import bulkcreateusers


class TestBulkCreateUsers(TestCase):
    def test_get_or_create_users_works(self):
        User.objects.create_user(
            'test_user', email='existing_user@gsa.gov')
        email_addresses = [
            'user1@gsa.gov', 'user2@gsa.gov', 'existing_user@gsa.gov']

        results = bulkcreateusers.get_or_create_users(email_addresses)
        users = User.objects.all()

        self.assertEqual(len(results), len(email_addresses))
        self.assertEqual(len(results), len(users))
        for u in users:
            self.assertIn(u.email, email_addresses)

    def test_get_or_create_users_skips_empty_strings(self):

        results = bulkcreateusers.get_or_create_users(['', 'boop@beep'])
        users = User.objects.all()

        self.assertEqual(len(results), 1)
        self.assertEqual('boop@beep', users[0].email)

    def test_add_users_to_group_works(self):
        user = User.objects.create_user('test_user', email='test@gsa.gov')
        group = Group(name='Test Group')
        group.save()
        bulkcreateusers.add_users_to_group(group, [user])
        group_users = group.user_set.all()
        self.assertEqual(len(group_users), 1)
        self.assertIn(user, group_users)
