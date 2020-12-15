import djclick as click

from django.contrib.auth.models import User, Group
from django.db import transaction
from django.core.management.base import CommandError


class DryRunFinished(Exception):
    pass


def get_or_create_users(email_addresses):
    users = []
    for email in email_addresses:
        if not email:
            continue
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create_user(
                username=email.split('@')[0],
                email=email
            )
        users.append(user)
    return users


def add_users_to_group(group, users):
    for u in users:
        group.user_set.add(u)
    group.save()


@click.command()
@click.argument('user_file', type=click.File('r'))
@click.option('--group', 'groupname', type=click.STRING,
              help='Name of group to which all users should be added')
@click.option('--dryrun', default=False, is_flag=True,
              help='If set, no changes will be made to the database')
def command(user_file, groupname, dryrun):
    '''
    Bulk creates users from email addresses in the the specified text file,
    which should contain one email address per line.
    If the optional "--group <GROUPNAME>" argument is specified, then all the
    users (either found or created) are added to the matching group.
    '''
    if dryrun:
        click.echo('Starting dry run (no database records will be modified).')

    if groupname:
        try:
            group = Group.objects.get(name=groupname)
        except Group.DoesNotExist:
            raise CommandError(
                '"{}" group does not exist. Exiting.'.format(groupname))

    email_addresses = [s.strip() for s in user_file.readlines()]

    try:
        with transaction.atomic():
            users = get_or_create_users(email_addresses)
            click.echo(
                'Created (or found) {} user accounts.'.format(len(users)))
            if group:
                add_users_to_group(group, users)
                click.echo('Added users to "{}" group.'.format(groupname))
            if dryrun:
                raise DryRunFinished()
    except DryRunFinished:
        click.echo("Dry run complete.")
