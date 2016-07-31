from django.contrib import admin

from .models import Committee


class CommitteeAdmin(admin.ModelAdmin):
    search_fields = ('short_code', 'long_name')
    list_display = ('short_code', 'long_name')

admin.site.register(Committee, CommitteeAdmin)
