from django.db.models.signals import post_save
from django.dispatch import receiver

from .bot import sendmsg
from data_capture.models import SubmittedPriceList
from calc.site_utils import absolute_reverse


@receiver(post_save, sender=SubmittedPriceList)
def on_submittedpricelist_save(sender, created=False, instance=None,
                               **kwargs) -> None:
    if (created and instance and
            instance.status == SubmittedPriceList.STATUS_UNREVIEWED):
        url = absolute_reverse(
            'admin:data_capture_unreviewedpricelist_change',
            args=(instance.id,)
        )
        sendmsg(f'A new <{url}|price list> has been submitted!')
