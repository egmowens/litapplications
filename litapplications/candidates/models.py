from __future__ import unicode_literals

from django.db import models

from litapplications.committees.models import Committee

class Candidate(models.Model):
    STATUS_CHOICES = (
        (0, 'APPLICANT'),
        (1, 'PROPOSED'),
        (2, 'ACCEPTED'),
    )

    REVIEWED = 'Review complete'
    IN_PROCESS = 'Review in process'
    UNREVIEWED = 'Review not yet started'

    ala_id = models.CharField(max_length=15)
    first_name = models.CharField(max_length=15)
    last_name = models.CharField(max_length=30)
    status = models.IntegerField(choices=STATUS_CHOICES)
    email = models.EmailField()
    resume = models.TextField()
    other_info = models.TextField()
    memberships = models.TextField()
    state = models.CharField(max_length=3)
    country = models.CharField(max_length=20)
    notes = models.TextField()
    form_date = models.DateField()
    last_updated = models.DateField(auto_now=True)

    desired_comms = models.ManyToManyField(Committee,
        help_text='Committee(s) requested by this candidate',
        related_name='desired_comms')

    potential_comms = models.ManyToManyField(Committee,
        help_text='Committee(s) being considered by LITA Appointments',
        related_name='potential_comms')

    review_complete = models.BooleanField(default=False,
        help_text='Have recommendations been finalized?')

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        return '{self.first_name} {self.last_name}'.format(self=self)
    
    def review_status(self):
        if self.review_complete:
            return self.REVIEWED
        elif self.potential_comms:
            return self.IN_PROCESS
        else:
            return self.UNREVIEWED
