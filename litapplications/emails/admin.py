from django.contrib import admin

from .models import EmailMessage, EmailType


class EmailMessageAdmin(admin.ModelAdmin):
    list_display = ('address', 'emailtype', 'status')

admin.site.register(EmailMessage, EmailMessageAdmin)



class EmailTypeAdmin(admin.ModelAdmin):
    list_display = ('trigger',)

admin.site.register(EmailType, EmailTypeAdmin)
