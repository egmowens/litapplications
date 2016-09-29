from datetime import date, timedelta

from django.dispatch import receiver, Signal

from .models import (EmailType,
                     EmailMessage,
                     NEW_VOLUNTEER_FORM)


# Any code that wants email to be sent should send this signal.
signal_send_email = Signal(providing_args=["trigger", "candidate", "unit"])

# This function receives the email-sending signal and delegates to appropriate
# functions for fulfillment.
@receiver(signal_send_email)
def email_candidate(sender, trigger, candidate, unit, **kwargs):
    if trigger == NEW_VOLUNTEER_FORM:
        email_new_volunteer(candidate, unit)


# Fulfillment functions
# ------------------------------------------------------------------------------
#
# These functions handle constructing the emails for each trigger.
#
# Note that Heroku scheduler will check for unsent EmailMessages periodically
# and fire a management command to send them. Therefore there is *no need* to
# do any sort of sending here; constructing the message will suffice.
#
# Using Scheduler keeps email-sending out of the request/response loop and
# prevents timeouts, but is lighter-weight than celery - let's see if it works!


def email_new_volunteer(candidate, unit):
    """
    Acknowledge receipt of new volunteer form, if we have not previously
    acknowledged receipt of an application to this unit. This is intended for
    'welcome to the system, here is the process' sorts of emails, not 'we got
    your form, thanks' sorts.

    This will send whatever emails are attached to the NEW_VOLUNTEER_FORM
    trigger.
    """
    # 1) Can we email this candidate?
    if not candidate.email:
        return

    # 2) Should we email this candidate? (Have they recently applied to a
    # committee attached to this unit?)
    recently = date.today() - timedelta(days=30)
    eligible_appts = candidate.appointments.filter(
        form_date__gte=recently, unit=unit)
    if not eligible_appts:
        return

    # (Hopefully there's just one emailtype, but we haven't enforced that in the
    # db.)
    emailtypes = EmailType.objects.filter(trigger=NEW_VOLUNTEER_FORM, unit=unit)

    # 3) Have we already emailed this candidate? If not, we can, should, and
    # will send email!
    for emailtype in emailtypes:
        if EmailMessage.objects.filter(
            emailtype=emailtype,
            address=candidate.email):

            pass

        else:
            # This might send an email to the same candidate more than once,
            # if their email address has changed. We're going to decide that's
            # okay - people frequently forget to update their email addresses
            # with ALA as they change jobs, etc., so the previous email may have
            # gone to an inbox that no longer exists.
            email = EmailMessage()
            email.address = candidate.email
            email.first_name = candidate.first_name
            email.last_name = candidate.last_name
            email.emailtype = emailtype
            email.save()
