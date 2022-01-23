from django.contrib import admin
from .models import Category

# Register your models here.

#making the slug field prepoplated field with the value of category name

class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('category_name',)}


admin.site.register(Category,CategoryAdmin)
