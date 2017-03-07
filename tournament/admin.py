from django.contrib import admin

from .models import Variable, Team, Entry

class EntryInline(admin.TabularInline):
    model= Entry
    extra = 0

class VariableAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'coefficient']})]
    inlines = [EntryInline]
    list_display = ['name', 'coefficient']
    list_filter = ['name']
    search_fields = ['name']

class TeamAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name']})]
    inlines = [EntryInline]
    list_display = ['name']
    list_filter = ['name']
    search_fields = ['name']


admin.site.register(Variable, VariableAdmin)
admin.site.register(Team, TeamAdmin)
