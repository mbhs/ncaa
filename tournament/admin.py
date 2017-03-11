from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Variable, Team, Entry, Coefficient

class CoefficientAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['value', 'variable','user']})]
    list_display = ['value', 'variable','user']
    list_filter = ['value']
    search_fields = ['value']

class EntryInline(admin.TabularInline):
    model= Entry
    extra = 0

class VariableAdmin(admin.ModelAdmin):
    fieldsets = [
        (None, {'fields': ['name', 'stdev', 'mean']})]
    inlines = [EntryInline]
    list_display = ['name', 'stdev', 'mean']
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
admin.site.register(Coefficient, CoefficientAdmin)
