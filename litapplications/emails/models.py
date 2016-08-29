from django.db import models

# Trigger conditions
# ------------------------------------------------------------------------------
#
# These are conditions under which we may want to send emails. They're named
# constants, for use in triggers and models below. Maximum length of the
# human-readable string is 30 chars. They're here instead of in triggesr.py
# to avoid circular imports.

NEW_VOLUNTEER_FORM = 'NEW_VOLUNTEER_FORM'


class EmailType(models.Model):
    """
    Allows a user to associate a trigger function with an email subject/body.
    This lets us send that email when that trigger happens (though you must
    separately write the logic for so doing).
    """

    EMAIL_TRIGGERS = (
        (NEW_VOLUNTEER_FORM, NEW_VOLUNTEER_FORM),
    )

    trigger = models.CharField(max_length=30, choices=EMAIL_TRIGGERS)
    subject = models.CharField(max_length=50,
        help_text='The subject line of your email. {first_name} '
            'and {last_name} are available.')
    body = models.TextField(
        help_text='The body of your email. {first_name} and '
            '{last_name} are available.')
    from_name = models.CharField(max_length=50,
        help_text='Name of the person that this email should appear to be from')

    class Meta:
        verbose_name = "EmailType"
        verbose_name_plural = "EmailTypes"


    def __str__(self):
        return '{self.trigger} from {self.from_name}'.format(self=self)



class EmailMessage(models.Model):
    address = models.EmailField()
    first_name = models.CharField(max_length=15, blank=True)
    last_name = models.CharField(max_length=30, blank=True)
    emailtype = models.ForeignKey(EmailType)
    status = models.IntegerField(blank=True, null=True,
        help_text='Status returned by sendgrid upon trying to send this. '
            'Blank if no attempt has been made to send.')

    class Meta:
        verbose_name = "EmailMessage"
        verbose_name_plural = "EmailMessages"


    def __str__(self):
        return '{self.emailtype.trigger} for {self.address} ' \
            '(status {self.status})'.format(self=self)


    def has_been_sent(self):
        # See https://sendgrid.com/docs/Glossary/email_error_messages.html
        # for status codes. Only 250 is a successful sending.
        return self.status == 250


    def has_failed(self):
        # These are hard failures: ones which won't be retried. Sendgrid will
        # retry temporary failures, so we ignore them.
        return self.status in [550, 551, 552, 554]
    