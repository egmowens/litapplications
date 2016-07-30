from __future__ import unicode_literals

from django.db import models

class Committee(models.Model):

    class Meta:
        verbose_name = "Committee"
        verbose_name_plural = "Committees"

    def __str__(self):
        pass
    
        