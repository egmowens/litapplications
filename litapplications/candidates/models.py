from __future__ import unicode_literals

from django.db import models


class Candidate(models.Model):
    STATUS_CHOICES = (
        (0, 'APPLICANT'),
        (1, 'PROPOSED'),
        (2, 'ACCEPTED'),
    )
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

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"

    def __str__(self):
        pass
    