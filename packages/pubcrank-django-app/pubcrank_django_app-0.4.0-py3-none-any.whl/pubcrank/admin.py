from django.contrib import admin

from pubcrank.models import Page

@admin.register(Page)
class PageAdmin(admin.ModelAdmin):
  list_display = ('path', )
