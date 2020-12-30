from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.db import transaction

from calc.utils import get_permissions_from_ns_codenames

BULK_UPLOAD_PERMISSION = 'contracts.add_bulkuploadcontractsource'
PRICE_LIST_UPLOAD_PERMISSION = 'data_capture.add_submittedpricelist'
ANALYZE_PRICES_PERMISSION = PRICE_LIST_UPLOAD_PERMISSION  # May change later.
VIEW_ATTEMPT_PERMISSION = 'data_capture.change_attemptedpricelistsubmission'

ROLES = {}

# Devs: If any roles are added or modified, please also update
# the "Authentication and Authorization" section of docs/auth.md.

ROLES['Data Administrators'] = set([
    ANALYZE_PRICES_PERMISSION,
    'auth.add_user',
    'auth.change_user',
    BULK_UPLOAD_PERMISSION,
    'contracts.add_schedulemetadata',
    'contracts.change_schedulemetadata',
    'contracts.delete_schedulemetadata',
    'data_capture.change_submittedpricelist',
    'data_capture.change_submittedpricelistrow',
    'data_capture.change_unreviewedpricelist',
    'data_capture.change_approvedpricelist',
    'data_capture.change_retiredpricelist',
    'data_capture.change_rejectedpricelist',
])

ROLES['Contract Officers'] = set([
    ANALYZE_PRICES_PERMISSION,
    PRICE_LIST_UPLOAD_PERMISSION,
    'data_capture.add_submittedpricelistrow',
])

ROLES['Technical Support Specialists'] = set([
    VIEW_ATTEMPT_PERMISSION,
])

# Data Administrators should also have any perms that Contract Officers do
ROLES['Data Administrators'].update(ROLES['Contract Officers'])


class Command(BaseCommand):
    help = '''\
    Initializes some helpful initial permission groups.
    '''

    def set_perms(self, groupname, perms):
        self.stdout.write("Setting permissions for group '%s'." % groupname)
        if self.verbosity >= 2:
            self.stdout.write("  Permissions: %s" % ', '.join(perms))
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            self.stdout.write("  Group does not exist, creating it.")
            group = Group(name=groupname)
            group.save()
        try:
            group.permissions = get_permissions_from_ns_codenames(perms)
            group.save()
        except Exception as e:
            self.stderr.write(f"Error stroing group  {e}.")
            print(e)

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.verbosity = int(kwargs['verbosity'])
        for groupname, perms in ROLES.items():
            self.set_perms(groupname, perms)
        self.stdout.write("Done.")
        self.stdout.write("Please do not manually change these "
                          "groups; they may be updated in the future.")
