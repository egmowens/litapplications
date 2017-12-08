from __future__ import unicode_literals

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.timezone import now

from litapplications.candidates.models import Appointment

from .units import Unit                    


class Committee(models.Model):

    short_code = models.CharField(max_length=15, blank=True, unique=True)
    long_name = models.CharField(max_length=50, blank=True)
    min_appointees = models.IntegerField(null=True, blank=True)
    max_appointees = models.IntegerField(null=True, blank=True)
    owner = models.ForeignKey(User, null=True, blank=True)
    charge = models.URLField(null=True, blank=True,
        help_text='Link to committee charge')
    notes = models.TextField(blank=True, help_text='Skills the committee is '
        'looking for, special requirements, etc.')
    unit = models.ForeignKey(Unit, null=True, blank=True)

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"
        ordering = ['long_name']

    def __str__(self):
        return self.long_name


    def clean(self):
        super(Committee, self).clean()
        if self.max_appointees < self.min_appointees:
            raise ValidationError('The maximum number of appointees cannot be '
                'less than the minimum number of appointees.')


    def get_absolute_url(self):
        return reverse_lazy('committees:detail', args=[self.pk])

    @property
    def is_fully_appointed(self):
        if (self.appointments.filter(status__in=[
                Appointment.RECOMMENDED, Appointment.ACCEPTED],
                year_start__gte=now().year
            ).count() >= self.min_appointees and 
            self.min_appointees is not None):

            return True
        else:
            return False


    @property
    def is_fully_staffed(self):
        if (len(self.members()) >= self.min_appointees
            and self.min_appointees is not None):

            return True
        else:
            return False

    def members(self, year=None):
        # If no year is given, return next year's members.
        if not year:
            year = Committee.current_ala_year() + 2

        appts = self.appointments.filter(
            status=Appointment.ACCEPTED,
            year_start__lt=year,
            year_end__gte=year)

        return list(set([appt.candidate for appt in appts]))


    @staticmethod
    def current_ala_year():
        if now().month < 7:
            return now().year - 1
        else:
            return now().year
