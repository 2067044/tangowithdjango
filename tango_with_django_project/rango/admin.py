from django.contrib import admin
from rango.models import Category, Page


class PageAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'url')
    list_filter = ['category']  # filter sidebar
    search_fields = ['title']   # search bar on title


class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

# This registers the models and makes them visible in the admin panel
admin.site.register(Category, CategoryAdmin)
admin.site.register(Page, PageAdmin)  # pass the class here so that the admin panel gets changed
