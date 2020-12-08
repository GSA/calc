from typing import NamedTuple, List
from django.conf import settings
from django.http import Http404, HttpResponseRedirect
from django.contrib.auth import login
from django.contrib.auth.models import User, Group


class SampleUser(NamedTuple):
    username: str
    desc: str
    is_staff: bool
    is_superuser: bool
    groups: List[str]

    @property
    def email(self):
        return f'{self.username}@example.com'

    @property
    def group_pks(self):
        return [
            Group.objects.filter(name=groupname).get().pk
            for groupname in self.groups
        ]


SAMPLE_USERS = [
    SampleUser('co', 'Contract officer', False, False, ['Contract Officers']),
    SampleUser('data-admin', 'Data administrator', True, False, ['Data Administrators']),
    SampleUser('tech-support', 'Technical support specialist', True, False, [
        'Technical Support Specialists']),
    SampleUser('superuser', 'Superuser', True, True, []),
]

DEBUG_ONLY_MSG = 'Sample users are only available in DEBUG mode!'


def get_or_create_sample_user(username: str) -> User:
    sus = [su for su in SAMPLE_USERS if su.username == username]
    if not sus:
        raise Http404('Sample user not found!')

    su = sus[0]

    queryset = User.objects.filter(username=su.username)
    if not queryset.exists():
        user = User.objects.create_user(su.username)

    # Setting all the properties of the sample user every time they
    # log in makes development easier since we can just edit
    # SAMPLE_USERS anytime and be confident that the database will be
    # in sync with their values.
    user = queryset.get()
    user.email = su.email
    user.is_staff = su.is_staff
    user.is_superuser = su.is_superuser
    user.groups = su.group_pks
    user.save()

    return user


def login_sample_user(request, username):
    '''
    This is a development-only view that logs in a sample user from
    the SAMPLE_USERS list.

    Because it's development-only, it cuts a lot of corners that a
    production view wouldn't, e.g.:

    * Server state is changed despite this being a HTTP GET.
    * Trades efficiency for ease of development/debugging.
    * Very little input sanitization.

    That said, we make very sure that we are in DEBUG mode and
    raise a 404 if we're not.
    '''

    if not (settings.DEBUG and not settings.HIDE_DEBUG_UI):
        raise Http404(DEBUG_ONLY_MSG)

    user = get_or_create_sample_user(username)
    login(request, user)

    # A production view would sanitize this, but we'll just use it as-is.
    next_url = request.GET.get('next', '/')

    return HttpResponseRedirect(next_url)
