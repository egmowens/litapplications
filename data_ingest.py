# read file (for now, assume Vlntr Export)
# parse

import argparse
from bs4 import BeautifulSoup
import logging

from litapplications.candidates.models import Candidate, Appointment
from litapplications.committees.models import Committee

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

def update_fields(candidate, entity):
    candidate.first_name = entity[FIRST_NAME_KEY]
    candidate.last_name = entity[LAST_NAME_KEY]
    candidate.email = entity[EMAIL]
    candidate.resume = entity[EXPERTISE_KEY]
    candidate.ala_appointments = entity[APPOINTMENTS_KEY]
    candidate.other_info = entity[OTHER_INFO_KEY]
    candidate.memberships = entity[MEMBERSHIPS_KEY]
    candidate.state = entity[STATE_KEY]
    candidate.country = entity[COUNTRY_KEY]
    candidate.form_date = entity[STATUS_DATE_KEY]


def create_candidate(entity):
    candidate = Candidate()
    candidate.ala_id = entity[ALA_ID_KEY]
    update_fields(candidate, entity)
    candidate.save()

    return candidate


def process_entity(entity):
    warnings = []

    ala_id = entity[ALA_ID_KEY]

    # If ALA ID is new, create a Candidate accordingly
    if not Candidate.objects.filter(ala_id=ala_id).count():
        candidate = create_candidate(entity)
    else:
        candidate = Candidate.objects.get(ala_id=ala_id)
        update_fields(candidate, entity)
        candidate.save()

    if not ((candidate.first_name == entity[FIRST_NAME_KEY]) and
            (candidate.last_name == entity[LAST_NAME_KEY])):
        warnings.append('Candidate has changed names - verify info is correct')

    # Find the referenced committee (and don't do anything if we can't)
    committee_code = entity[COMMITTEE_KEY]

    try:
        committee = Committee.objects.get(short_code=committee_code)
    except Committee.DoesNotExist:
        logger.exception()
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

    # Status defaults to APPLICANT, so it needn't be specified in that case.
    if entity[STATUS_KEY] == PROPOSED:
        appointment.status = Appointment.RECOMMENDED
    elif entity[STATUS_KEY] == COMMITTEE:
        appointment.status = Appointment.ACCEPTED

    appointment.save()


def parse_file(filename):
    with open(filename) as html:
        soup = BeautifulSoup(html.read())

    table = soup.find('table')
    keys = [header.text.strip() for header in table.find_all('th')]

    for row in table.find_all('tr'):
        values = [val.text.encode('utf8') for val in row.find_all('td')]
        entity = dict(zip(keys, values))
        process_entity(entity)


parser = argparse.ArgumentParser()
parser.add_argument('filename')
args = parser.parse_args()

parse_file(args.filename)
