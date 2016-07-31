from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.db import models

from litapplications.candidates.models import Appointment


class Committee(models.Model):

    short_code = models.CharField(max_length=15, blank=True)
    long_name = models.CharField(max_length=50, blank=True)
    min_appointees = models.IntegerField(null=True, blank=True)
    max_appointees = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(User)
    charge = models.URLField(null=True, blank=True,
        help_text='Link to committee charge')
    notes = models.TextField(blank=True, help_text='Skills the committee is '
        'looking for, special requirements, etc.')

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    def __str__(self):
        return self.long_name


    def is_fully_appointed(self):
        if self.appointments.filter(status__in=[
                Appointment.RECOMMENDED, Appointment.ACCEPTED]
            ).count() >= self.min_appointees:

            return True
        else:
            return False

    def is_fully_staffed(self):
        if self.appointments.filter(
            status__in=[Appointment.ACCEPTED]).count() >= self.min_appointees:

            return True
        else:
            return False
