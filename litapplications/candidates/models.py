from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.db import models


class Candidate(models.Model):
    REVIEWED = 'Review complete'
    IN_PROCESS = 'Review in process'
    UNREVIEWED = 'Review not yet started'

    ala_id = models.CharField(max_length=15)
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
        ordering = ['-form_date', 'last_updated']

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


class Appointment(models.Model):
    APPLICANT = 'Applicant'
    POTENTIAL = 'Potential'
    RECOMMENDED = 'Recommended'
    ACCEPTED = 'Accepted'
    DECLINED = 'Declined'

    STATUS_CHOICES = (
        (APPLICANT, APPLICANT),   # Candidate requested an appointment to this comm.
        (POTENTIAL, POTENTIAL),   # Committee is considering candidate for comm.
        (RECOMMENDED, RECOMMENDED), # Committee advises VP to appoint this one.
        (ACCEPTED, ACCEPTED),    # Candidate has accepted appointment.
        (DECLINED, DECLINED),    # Candidate has declined appointment.
    )

    candidate = models.ForeignKey(Candidate, related_name='appointments')
    # We have to reference by name rather than by importing Committee, because
    # doing so would result in circular imports.
    committee = models.ForeignKey('committees.Committee',
        related_name='appointments')
    status = models.CharField(max_length=12,
        choices=STATUS_CHOICES,
        default=APPLICANT)

    class Meta:
        verbose_name = "Appointment"
        verbose_name_plural = "Appointments"

    def __str__(self):
        return '{self.candidate} for {self.committee}'.format(self=self)
    