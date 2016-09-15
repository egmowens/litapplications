from __future__ import unicode_literals
from datetime import date, timedelta

from django.core.urlresolvers import reverse_lazy
from django.db import models
from django.utils.html import mark_safe

from litapplications.committees.models.units import Unit


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

    TYPE_PUBLIC = 0
    TYPE_ACADEMIC = 1
    TYPE_SCHOOL = 2
    TYPE_SPECIAL = 3
    TYPE_STUDENT = 4
    TYPE_VENDOR = 5
    TYPE_OTHER = 6
    TYPE_UNKNOWN = 7

    LIBRARY_TYPE_IMAGES = {
        TYPE_PUBLIC: '/static/img/icons/librarysymbol.png',
        TYPE_ACADEMIC: '/static/img/icons/school.png',
        TYPE_SCHOOL: '/static/img/icons/lecturer.svg',
        TYPE_SPECIAL: '/static/img/icons/snowflake.svg',
        TYPE_STUDENT: '/static/img/icons/mortarboard.svg',
        TYPE_VENDOR: '/static/img/icons/briefcase.svg',
        TYPE_OTHER: '/static/img/icons/book.svg',
        TYPE_UNKNOWN: '/static/img/icons/blank.svg',
    }

    LIBRARY_TYPE_CHOICES = (
        (TYPE_PUBLIC, 'Public librarian'),
        (TYPE_ACADEMIC, 'Academic librarian'),
        (TYPE_SCHOOL, 'School librarian'),
        (TYPE_SPECIAL, 'Special librarian'),
        (TYPE_STUDENT, 'Student'),
        (TYPE_VENDOR, 'Vendor'),
        (TYPE_OTHER, 'Other'),
        (TYPE_UNKNOWN, 'Unknown'),
    )

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
    library_type = models.IntegerField(choices=LIBRARY_TYPE_CHOICES,
        default=TYPE_UNKNOWN)
    chair_notes = models.TextField(blank=True,
        help_text='Any information from the chair on why the committee should '
            'particularly consider this candidate.')

    class Meta:
        verbose_name = "Candidate"
        verbose_name_plural = "Candidates"
        ordering = ['first_name', 'last_name']

    #
    # Methods
    # --------------------------------------------------------------------------

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


    def get_html_name(self):
        if self.starred:
            star = ' <span class="glyphicon glyphicon-star text-primary"></span>'
        else:
            star = ''

        library_type = '<img class="library-type-icon" src="{src}" alt="{alt}">'.format(
            src=self.library_type_icon, alt=self.get_library_type_display())

        return mark_safe('{type}{name}{star}'.format(
            type=library_type, name=self, star=star))


    @property
    def library_type_icon(self):
        return self.LIBRARY_TYPE_IMAGES[self.library_type]


    @property
    def starred(self):
        # Any candidate with notes from the chair can be shown as starred in the
        # interface using this property.
        return bool(self.chair_notes)

    #
    # Managers
    # ---------------------------------------------------------------------------

    even_obsolete = models.Manager()
    objects = RecentVolunteersManager()



class Note(models.Model):
    candidate = models.ForeignKey(Candidate)
    unit = models.ForeignKey(Unit)
    text = models.TextField()
    privileged = models.BooleanField(help_text='Is this note written by '
        'someone with special authority over the appointments process, '
        'like an executive director or chair')

    class Meta:
        verbose_name = "Note"
        verbose_name_plural = "Notes"

    def __str__(self):
        pass



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
