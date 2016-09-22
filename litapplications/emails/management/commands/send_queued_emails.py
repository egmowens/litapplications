import logging
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Email, Content, Mail

from django.conf import settings
from django.core.management.base import BaseCommand

from ...models import EmailMessage

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sends queued emails'

    def handle(self, *args, **options):
        if not hasattr(settings, 'SENDGRID_API_KEY'):
            return

        if not settings.SENDGRID_API_KEY:
            return

        sg_api = SendGridAPIClient(apikey=settings.SENDGRID_API_KEY)

        msg_ids = EmailMessage.objects.filter(status__isnull=True).values('id')

        for msg_id in msg_ids:
            # We're going to be altering messages in the course of this loop,
            # so let's iterate over the IDs and not the message objects
            # themselves.
            # Note that values() returns a list of dicts, {'field_name': value}.
            message = EmailMessage.objects.get(id=msg_id['id'])

            from_email = Email("andromeda.yelton@gmail.com")
            to_email = Email(message.address)

            try:
                subject = message.emailtype.subject.format(
                    first_name=message.first_name,
                    last_name=message.last_name)
            except KeyError:
                # If users have screwed up entering {first_name} or {last_name},
                # format() will throw a KeyError.
                subject = 'About your ALA committee volunteering'

            try:
                body = message.emailtype.body.format(
                    first_name=message.first_name,
                    last_name=message.last_name)
            except KeyError:
                # This may look like a bad mail merge, but we can't anticipate
                # a substitute.
                body = message.emailtype.body
            content = Content("text/plain", body)

            mail = Mail(from_email, subject, to_email, content)

            response = sg_api.client.mail.send.post(request_body=mail.get())

            message.status = response.status_code
            message.save()
