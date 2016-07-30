# read file (for now, assume Vlntr Export)
# parse

import argparse
from bs4 import BeautifulSoup

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

def process_entity(entity):
    ala_id = entity[ALA_ID_KEY]

    for key in DATA_KEYS:
        print entity[key]

    print '\n\n'

    # If ALA ID is new, create a Candidate accordingly

    # If ALA ID is not new...
        # Check name. If it's different, flag for human review.
        # Otherwise, update the Candidate
            # if the status doesn't match internal status, flag for human review
            # note that there's no way to tell they've stopped being interested...

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
