import logging
from django.dispatch import receiver
from django.db.models.signals import pre_save, post_save, m2m_changed
from django.core.signals import setting_changed
from django.contrib.auth.models import User, Group
from django.contrib.admin.models import (
    LogEntry, ADDITION, CHANGE, DELETION
)

from .models import SubmittedPriceList
from .schedules import registry


logger = logging.getLogger('calc')


@receiver(pre_save, sender=SubmittedPriceList)
def log_price_list_creation(sender, instance=None, **kwargs):
    if instance is not None and instance.pk is None:
        logger.info(
            f'Creating SubmittedPriceList for {instance.contract_number}, '
            f'submitted by {instance.submitter}.'
        )


@receiver(post_save, sender=LogEntry)
def adminlog_post_save(sender, instance, **kwargs):
    """Django's admin already logs when edits are made. Pass that along to our
    logging system."""

    if instance.action_flag == ADDITION:
        logger.info("%s created %s '%s'", instance.user.username,
                    instance.content_type, instance.object_repr)
    elif instance.action_flag == DELETION:
        logger.info("%s deleted %s '%s'", instance.user.username,
                    instance.content_type, instance.object_repr)
    elif instance.action_flag == CHANGE:
        logger.info("%s changed %s '%s': %s", instance.user.username,
                    instance.content_type, instance.object_repr,
                    instance.change_message)


@receiver(m2m_changed, sender=User.groups.through)
@receiver(m2m_changed, sender=User.user_permissions.through)
@receiver(m2m_changed, sender=Group.permissions.through)
def log_m2m_change(sender, instance, action, reverse, model, pk_set, **kwargs):
    """Log changes for many-to-many fields, notably around permissions and
    groups"""

    model_name = model._meta.verbose_name_plural
    instance_model = instance._meta.verbose_name
    if action == 'post_add':
        objects_added = list(model.objects.filter(pk__in=pk_set))
        logger.info("%s given to %s '%s': %s", model_name, instance_model,
                    instance, objects_added)
    elif action == 'post_remove':
        objects_added = list(model.objects.filter(pk__in=pk_set))
        logger.info("%s removed from %s '%s': %s", model_name, instance_model,
                    instance, objects_added)
    elif action == 'post_clear':
        logger.info("All %s removed from %s '%s'", model_name, instance_model,
                    instance)


@receiver(setting_changed)
def repopulate_registry(setting, **kwargs):
    '''
    Django signal handler to re-populate the registry whenever anything
    (presumably a test case) modifies settings.DATA_CAPTURE_SCHEDULES.
    '''

    if setting == "DATA_CAPTURE_SCHEDULES":
        registry.populate_from_settings()
