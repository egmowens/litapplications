from django.db import models


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
            ('appointment__can_recommend',
                'Can recommend appointments to unit committees'),
            ('appointment__can_finalize',
                'Can finalize appointments to unit committees'),
            ('email__can_send',
                'Can send email for unit-specific triggers'),
            ('note__can_make_candidate_note',
                'Can make notes on candidates for unit committees'),
            ('note__can_make_privileged_note',
                'Can make privileged notes on candidates for unit committees'),
        )


    def __str__(self):
        return self.name
