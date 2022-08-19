from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html

# Register your models here.

from .models import Account,UserProfile



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


class UserProfileAdmin(admin.ModelAdmin):
    def thumbnail(self,object):
        return format_html('<img src={} width="30" height="30" style="border-radius:50%;">'.format(object.profile_picture.url))
    thumbnail.short_description  = 'Profile Picture'

    list_display = ('thumbnail','user','city','state','country')


admin.site.register(Account,AccountAdmin)
admin.site.register(UserProfile,UserProfileAdmin)

