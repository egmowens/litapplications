from guardian.admin import GuardedModelAdmin

from django.contrib import admin

from .models.committees import Committee
from .models.units import Unit

class CommitteeAdmin(admin.ModelAdmin):
    search_fields = ('short_code', 'long_name')
    list_display = ('short_code', 'long_name')

admin.site.register(Committee, CommitteeAdmin)



class UnitAdmin(GuardedModelAdmin):
    search_fields = ('name',)
    list_display = ('name',)

admin.site.register(Unit, UnitAdmin)


