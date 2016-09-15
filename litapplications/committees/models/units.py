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

    def __str__(self):
        return self.name
