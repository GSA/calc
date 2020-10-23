import unittest

from django.test import TestCase, override_settings
from django.contrib.auth.models import User, Group

from calc.utils import get_permissions_from_ns_codenames


class BaseTestCase(TestCase):
    def assertHasMessage(self, res, tag, content):
        msgs = list(res.context['messages'])
        self.assertEqual(len(msgs), 1)
        m = msgs[0]
        self.assertEqual(m.tags, tag)
        self.assertEqual(str(m), content)


@override_settings(
    # This will make tests run faster.
    PASSWORD_HASHERS=['django.contrib.auth.hashers.MD5PasswordHasher'],
    # Ignore our custom auth backend so we can log the user in via
    # Django 1.8's login helpers.
    AUTHENTICATION_BACKENDS=[
        'django.contrib.auth.backends.ModelBackend',
        # But also include UaaBackend so cg-django-uaa doesn't raise an
        # ImproperlyConfigured error.
        'uaa_client.authentication.UaaBackend',
    ],
)
class BaseLoginTestCase(BaseTestCase):
    def create_user(self, username, password=None, is_staff=False,
                    is_superuser=False, email=None, groups=()):
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )
        for groupname in groups:
            g = Group.objects.get(name=groupname)
            g.user_set.add(user)
            g.save()
        if is_staff:
            user.is_staff = True
            user.save()
        if is_superuser:
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user

    def login(self, username='foo', is_staff=False, is_superuser=False,
              groups=(), permissions=None):
        user = self.create_user(username=username, password='bar',  # nosec
                                is_staff=is_staff,
                                is_superuser=is_superuser,
                                groups=groups)
        if permissions:
            user.user_permissions = get_permissions_from_ns_codenames(
                permissions)
            user.save()
        assert self.client.login(username=username, password='bar')  # nosec
        return user


class ProtectedViewTestCase(BaseLoginTestCase):
    url = None

    def assertRedirectsToLogin(self, url):
        res = self.client.get(url)
        self.assertEqual(res.status_code, 302)
        self.assertEqual(
            res['Location'],
            '/auth/login?next=%s' % url
        )

    def test_login_is_required(self):
        if not self.url:
            raise unittest.SkipTest()
        self.assertRedirectsToLogin(self.url)
