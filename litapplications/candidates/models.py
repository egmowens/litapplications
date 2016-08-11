from __future__ import unicode_literals
from datetime import date, timedelta

from django.core.urlresolvers import reverse_lazy
from django.db import models



class RecentVolunteersManager(models.Manager):
    """
    This class will act as the default manager for the Candidate model.

    It filters out candidates who do not have a recent volunteer application
    on file, unless we have been actively considering them. The ALA database
    does not clear out old applications, but we don't actually want to be
    considering candidates who have not volunteered recently.
    """
    def get_queryset(self):
        one_year_ago = date.today() - timedelta(days=365)
        # Query = recent candidates |or| candidates being considered.
        query = models.Q(form_date__gte=one_year_ago) | models.Q(
                    appointments__status__in=[
                        Appointment.POTENTIAL, Appointment.RECOMMENDED
                    ])
        return super(RecentVolunteersManager, self).get_queryset().filter(
            query).distinct()



class Candidate(models.Model):
    REVIEWED = 'Review complete'
    IN_PROCESS = 'Review in process'
    UNREVIEWED = 'Review not yet started'

    ala_id = models.CharField(max_length=15, unique=True)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=30)
    email = models.EmailField(blank=True)
    resume = models.TextField(blank=True)
    ala_appointments = models.TextField(blank=True) # Historical + current.
    other_info = models.TextField(blank=True)
    memberships = models.TextField(blank=True)
    state = models.CharField(max_length=3, blank=True)
    country = models.CharField(max_length=20, blank=True)
    notes = models.TextField(blank=True)
    form_date = models.DateField()
    last_updated = models.DateField(auto_now=True)

    review_complete = models.BooleanField(default=False,
        help_text='Have recommendations been finalized?')

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"
        ordering = ['first_name', 'last_name']

    #
    # Methods
    # ---------------------------------------------------------------------------

    def __str__(self):
        return '{self.first_name} {self.last_name}'.format(self=self)
    

    def get_absolute_url(self):
        return reverse_lazy('candidates:detail', args=[self.pk])


    def place_of_origin(self):
        if self.country and self.state:
            return '{self.state}, {self.country}'.format(self=self)
        elif self.country and not self.state:
            return '{self.country}'.format(self=self)
        elif self.state and not self.country:
            return '{self.state}'.format(self=self)
        else:
            return 'unknown place of residence'

    def review_status(self):
        if self.review_complete:
            return self.REVIEWED
        elif self.appointments.count():
            return self.IN_PROCESS
        else:
            return self.UNREVIEWED

    #
    # Managers
    # ---------------------------------------------------------------------------

    even_obsolete = models.Manager()
    objects = RecentVolunteersManager()



class Appointment(models.Model):
    APPLICANT = 'Applicant'
    POTENTIAL = 'Potential'
    RECOMMENDED = 'Recommended'
    NOPE = 'Not recommended'
    ACCEPTED = 'Accepted'
    DECLINED = 'Declined'
    SENT = 'Sent'

    STATUS_CHOICES = (
        (APPLICANT, APPLICANT),  # Candidate requested an appointment to this comm.
        (POTENTIAL, POTENTIAL),  # Committee is considering candidate for comm.
        (RECOMMENDED, RECOMMENDED), # Committee advises VP to appoint this one.
        (NOPE, NOPE),            # Committee advises VP not to appoint this one.
        (ACCEPTED, ACCEPTED),    # Candidate has accepted appointment.
        (DECLINED, DECLINED),    # Candidate has declined appointment.
        (SENT, SENT)             # Chair has sent appointment letter.
    )

    candidate = models.ForeignKey(Candidate, related_name='appointments')
    # We have to reference by name rather than by importing Committee, because
    # doing so would result in circular imports.
    committee = models.ForeignKey('committees.Committee',
        related_name='appointments')
    status = models.CharField(max_length=15,
        choices=STATUS_CHOICES,
        default=APPLICANT)
    locally_proposed = models.BooleanField(default=False,
        help_text='Set to True if the appointment was suggested by an '
        'Appointments Committee member - in this case you may have to ask the '
        'candidate to fill out a committee volunteer form, and also you should '
        'be careful of overwriting this.')

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"
        unique_together = (("candidate", "committee"),)

    def __str__(self):
        return '{self.candidate} for {self.committee}'.format(self=self)
    