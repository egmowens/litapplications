from guardian.shortcuts import get_objects_for_user

from django.db import models

APPOINTMENT__CAN_RECOMMEND = 'appointment__can_recommend'
APPOINTMENT__CAN_FINALIZE = 'appointment__can_finalize'
APPOINTMENT__CAN_SEE = 'appointment__can_see'
EMAIL__CAN_SEND = 'email__can_send'
NOTE__CAN_MAKE_CANDIDATE_NOTE = 'note__can_make_candidate_note'
NOTE__CAN_MAKE_PRIVILEGED_NOTE = 'note__can_make_privileged_note'
NOTE__CAN_SEE = 'note__can_see'
COMMITTEE__CAN_CREATE = 'committee__can_create'

# People with any of the following permissions should be able to see candidates
# with appropriately permissioned appointments or notes.
SHOULD_SEE_CANDIDATES = [APPOINTMENT__CAN_RECOMMEND,
                         APPOINTMENT__CAN_FINALIZE,
                         APPOINTMENT__CAN_SEE,
                         NOTE__CAN_MAKE_CANDIDATE_NOTE,
                         NOTE__CAN_MAKE_PRIVILEGED_NOTE,
                         NOTE__CAN_SEE]


def get_units_visible_to_user(user):
    """
    Given a user, return the set of units for which that user should be able to
    see candidate information.
    """
    unitlist = []
    for perm in SHOULD_SEE_CANDIDATES:
        units = get_objects_for_user(user,
            'committees.{perm}'.format(perm=perm))
        unitlist.extend(units)
    unitlist = list(set(unitlist)) # Make distinct
    return unitlist


def get_privileged_units(user):
    """
    Given a user, return the set of units for which that user can create
    committees.
    """
    units = get_objects_for_user(user,
        'committees.{perm}'.format(perm=COMMITTEE__CAN_CREATE))
    return units


class Unit(models.Model):
    """
    Represents a unit within ALA (e.g. LITA). Exists so that we can have unit-
    specific permissions (e.g. people can write notes visible only to other
    people in that unit; people can manage appointments only for a specific
    unit).
    """

    name = models.CharField(max_length=20)

    class Meta:
        verbose_name = "Unit"
        verbose_name_plural = "Units"
        ordering = ['name']
        permissions = (
            (APPOINTMENT__CAN_RECOMMEND,
                'Can recommend appointments to unit committees'),
            (APPOINTMENT__CAN_FINALIZE,
                'Can finalize appointments to unit committees'),
            (APPOINTMENT__CAN_SEE,
                'Can see (but not change) appointments to unit committees'),
            (EMAIL__CAN_SEND,
                'Can send email for unit-specific triggers'),
            (NOTE__CAN_MAKE_CANDIDATE_NOTE,
                'Can make notes on candidates for unit committees'),
            (NOTE__CAN_MAKE_PRIVILEGED_NOTE,
                'Can make privileged notes on candidates for unit committees'),
            (NOTE__CAN_SEE,
                'Can see (but not change) notes on candidates for unit committees'),
            (COMMITTEE__CAN_CREATE,
                'Can create committees belonging to this unit')
        )


    def __str__(self):
        return self.name
