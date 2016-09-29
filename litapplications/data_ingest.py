from bs4 import BeautifulSoup
from datetime import datetime
import logging
import time

from django.contrib import messages

from litapplications.candidates.models import Candidate, Appointment
from litapplications.committees.models.committees import Committee
from litapplications.emails.models import NEW_VOLUNTEER_FORM
from litapplications.emails.signals import signal_send_email

logger = logging.getLogger(__name__)

# This is the data we expect to see in the Vlntr Export files.
ALA_ID_KEY = 'ID'
FIRST_NAME_KEY = 'First Name'
LAST_NAME_KEY = 'Last Name'
COMMITTEE_KEY = 'Committee position'
STATUS_KEY = 'Status'
STATUS_DATE_KEY = 'Status Date'
EMAIL = 'Email'
APPOINTMENTS_KEY = 'ALA Appointments/Offices:'
EXPERTISE_KEY = 'List any Education and Experience you would like to share:'
OTHER_INFO_KEY = 'Other pertinent information you would like to share:'
MEMBERSHIPS_KEY = 'What Divisions and Roundtables do you belong to?'
STATE_KEY = 'State'
COUNTRY_KEY = 'Country'

DATA_KEYS = [ALA_ID_KEY, FIRST_NAME_KEY, LAST_NAME_KEY, COMMITTEE_KEY,
             STATUS_KEY, STATUS_DATE_KEY, EMAIL, APPOINTMENTS_KEY,
             EXPERTISE_KEY, OTHER_INFO_KEY, MEMBERSHIPS_KEY, STATE_KEY,
             COUNTRY_KEY]

# These are the statuses that an appointment application can have in the
# Vlntr Export file.
APPLICANT = 'APPLICANT'
PROPOSED = 'PROPOSED'
COMMITTEE = 'COMMITTEE'
STATUSES = [APPLICANT, PROPOSED, COMMITTEE]

def ingest_file(request, file_obj):
    warnings = []

    def _update_fields(candidate, entity):
        candidate.first_name = entity[FIRST_NAME_KEY]
        candidate.last_name = entity[LAST_NAME_KEY]
        candidate.email = entity[EMAIL]
        candidate.resume = entity[EXPERTISE_KEY]
        candidate.ala_appointments = entity[APPOINTMENTS_KEY]
        candidate.other_info = entity[OTHER_INFO_KEY]
        candidate.memberships = entity[MEMBERSHIPS_KEY]
        candidate.state = entity[STATE_KEY]
        candidate.country = entity[COUNTRY_KEY]
        raw_date = entity[STATUS_DATE_KEY]
        candidate.form_date = datetime(*(time.strptime(raw_date, "%b-%d-%Y")[0:6]))


    def _create_candidate(entity):
        candidate = Candidate()
        candidate.ala_id = entity[ALA_ID_KEY]
        _update_fields(candidate, entity)

        return candidate


    def _process_entity(entity):
        ala_id = entity[ALA_ID_KEY]

        # If ALA ID is new, create a Candidate accordingly
        try:
            # Make sure to look at ALL candidates, not just those exposed by
            # the default manager; if people have resubmitted forms after
            # having been dormant for a while, we want to update their
            # existing record, not try to create a new one (and fail when the
            # database rightly disallows two records with the same ALA ID).
            candidate = Candidate.even_obsolete.get(ala_id=ala_id)
            _update_fields(candidate, entity)
        except Candidate.DoesNotExist:
            candidate = _create_candidate(entity)

        candidate.save()

        if not ((candidate.first_name == entity[FIRST_NAME_KEY]) and
                (candidate.last_name == entity[LAST_NAME_KEY])):
            warnings.append('Candidate {candidate} has changed names - '
                'verify info is correct'.format(candidate=candidate))

        # Find the referenced committee (and don't do anything if we can't)
        committee_code = entity[COMMITTEE_KEY]

        try:
            committee = Committee.objects.filter(
                short_code__iexact=committee_code)[0] #case insensitive
        except IndexError:
            logger.exception('Could not find committee for {key}'.format(
                key=entity[COMMITTEE_KEY]))
            warnings.append('Could not find committee for {key}'.format(
                key=entity[COMMITTEE_KEY]))
            return

        try:
            appointment = Appointment.objects.get(
                committee=committee, candidate=candidate)
        except Appointment.DoesNotExist:
            appointment = Appointment()
            appointment.candidate = candidate
            appointment.committee = committee
            raw_date = entity[STATUS_DATE_KEY]
            appointment.form_date = datetime(*(
                time.strptime(raw_date, "%b-%d-%Y")[0:6]))

        # Status defaults to APPLICANT, so it needn't be specified in that case.
        if entity[STATUS_KEY] == PROPOSED:
            appointment.status = Appointment.RECOMMENDED
        elif entity[STATUS_KEY] == COMMITTEE:
            appointment.status = Appointment.ACCEPTED

        appointment.save()

        # This may be a new form; we might need to send a new candidate email.
        signal_send_email.send(
            sender=ingest_file,
            trigger=NEW_VOLUNTEER_FORM,
            candidate=candidate,
            unit=committee.unit)


    def parse_file(file_obj):
        soup = BeautifulSoup(file_obj.read())

        table = soup.find('table')
        keys = [header.text.strip() for header in table.find_all('th')]

        for row in table.find_all('tr'):
            values = [val.text.encode('utf8') for val in row.find_all('td')]
            if values:
                entity = dict(zip(keys, values))
                _process_entity(entity)

    parse_file(file_obj)

    if warnings:
        for warning in warnings:
            messages.add_message(request, messages.WARNING, warning)
    else:
        messages.add_message(request, messages.SUCCESS, 'All data processed :D')

