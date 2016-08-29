import logging
import sendgrid

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import EmailMessage

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends queued emails'

    def handle(self, *args, **options):
        if ((not hasattr(settings, 'SENDGRID_USERNAME')) or
            (not hasattr(settings, 'SENDGRID_PASSWORD'))):

            return

        sg_instance = sendgrid.SendGridClient(settings.SENDGRID_USERNAME,
                                              settings.SENDGRID_PASSWORD)

        msg_ids = EmailMessage.objects.filter(status__isnull=True).values('id')

        for msg_id in msg_ids:
            # We're going to be altering messages in the course of this loop,
            # so let's iterate over the IDs and not the message objects
            # themselves.
            message = EmailMessage.objects.get(id=msg_id)
            email = sg_instance.Mail()
            email.add_to(message.address)

            try:
                subject = message.emailtype.subject.format(
                    first_name=message.first_name,
                    last_name=message.last_name)
            except KeyError:
                # If users have screwed up entering {first_name} or {last_name},
                # format() will throw a KeyError.
                subject = 'LITA Appointments'
            email.set_subject(subject)

            try:
                body = message.emailtype.body.format(
                    first_name=message.first_name,
                    last_name=message.last_name)
            except KeyError:
                # This may look like a bad mail merge, but we can't anticipate
                # a substitute.
                body = message.emailtype.body
            email.set_text(body)

            message.set_from(message.emailtype.from_name)

            status, _ = sg_instance.send(message)
            message.status = status
            message.save()
