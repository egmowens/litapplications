from django.contrib import admin

from .models import Candidate, Appointment


class CandidateAdmin(admin.ModelAdmin):
    search_fields = ('first_name', 'last_name')
    list_display = ('first_name', 'last_name',)

admin.site.register(Candidate, CandidateAdmin)


class AppointmentAdmin(admin.ModelAdmin):
    search_fields = ('committee__long_name',
                     'candidate__first_name',
                     'candidate__last_name')
    list_display = ('committee', 'candidate', 'status')
    list_filter = ('status',)
    ordering = ('committee', 'status')

admin.site.register(Appointment, AppointmentAdmin)
