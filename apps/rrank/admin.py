from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.rrank.models import TeamNum


@admin.register(TeamNum)
class TeamNumAdmin(ModelAdmin):
    list_display = ['team', 'number']
    sortable_by = ['team', 'number']
    readonly_fields = ['team', 'number']
