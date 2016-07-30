from django.contrib import admin

from .models import Candidate


class CandidateAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    list_display = ('first_name', 'last_name',)

admin.site.register(Candidate, CandidateAdmin)
