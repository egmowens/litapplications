from django.db.models.signals import pre_save
from django.dispatch import receiver

from litapplications.candidates.models import Candidate

from .models import EmailType, EmailMessage, NEW_VOLUNTEER_FORM
from .tasks import queue_triggered_emails


def queue_triggered_emails(emailtypes, instance):
    """
    Accepts an iterable of EmailType instances to be sent, plus the a recipient
    candidate instance (possibly for a candidate not yet saved to the db).
    emailtypes may be empty; instance properties may be blank. Creates a record
    of emails to be sent. Heroku scheduler will check for expected, unsent
    emails and send them.
    """
    if instance.address:
        for emailtype in emailtypes:
            email = EmailMessage()
            email.address = instance.address
            email.first_name = instance.first_name
            email.last_name = instance.last_name
            email.emailtype = emailtype
            email.save()


# Trigger functions
# ------------------------------------------------------------------------------
#
# These are functions that should be fired when trigger conditions are met. They
# should all be @receivers of a relevant signal.
@receiver(pre_save, sender=Candidate)
def email_candidate_on_form_update(sender, instance, **kwargs):
    """
    Acknowledge receipt of new volunteer form.

    For new candidates, or existing candidates with new volunteer forms, this
    will send whatever emails are attached to the NEW_VOLUNTEER_FORM trigger.
    """
    emailtypes = EmailType.objects.filter(trigger=NEW_VOLUNTEER_FORM)
    if instance.id:
        # If this is an already existing candidate about to be updated, and
        # the date of the new volunteer form is greater than the date of the
        # existing one - that is, the candidate has submitted a new form -
        # send an email.
        orig_form_date = Candidate.even_obsolete.get(pk=instance.id).form_date
        current_form_date = instance.form_date
        if current_form_date > orig_form_date:
            queue_triggered_emails(emailtypes, instance)
    else:
        # No instance.id means this candidate hasn't been saved to the database
        # ever - it's a new candidate, so we should definitely send email.
        queue_triggered_emails(emailtypes, instance)
