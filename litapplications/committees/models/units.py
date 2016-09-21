from django.db import models

APPOINTMENT__CAN_RECOMMEND = 'appointment__can_recommend'
APPOINTMENT__CAN_FINALIZE = 'appointment__can_finalize'
EMAIL__CAN_SEND = 'email__can_send'
NOTE__CAN_MAKE_CANDIDATE_NOTE = 'note__can_make_candidate_note'
NOTE__CAN_MAKE_PRIVILEGED_NOTE = 'note__can_make_privileged_note'

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
            (EMAIL__CAN_SEND,
                'Can send email for unit-specific triggers'),
            (NOTE__CAN_MAKE_CANDIDATE_NOTE,
                'Can make notes on candidates for unit committees'),
            (NOTE__CAN_MAKE_PRIVILEGED_NOTE,
                'Can make privileged notes on candidates for unit committees'),
        )


    def __str__(self):
        return self.name
