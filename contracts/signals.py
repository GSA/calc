from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Contract


@receiver(post_save, sender=Contract)
def on_contract_save(sender, instance=None, **kwargs):
    if instance:
        Contract.objects.filter(pk=instance.id).update_search_index()
