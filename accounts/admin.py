from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

# Register your models here.

from .models import Account



#class to make the password field non-editable/read-only
#creating the links in Admin panel and readonly and other custom stuffs

class AccountAdmin(UserAdmin):
    list_display = ('email','first_name','last_name','username','last_login','date_joined','is_active')
    list_display_links = ('email','first_name','last_name')
    readonly_fields = ('last_login','date_joined')
    ordering = ('-date_joined',)
    filter_horizontal = ()   #this parameters are needed for custom usermodel
    list_filter = ()
    fieldsets = ()


admin.site.register(Account,AccountAdmin)
