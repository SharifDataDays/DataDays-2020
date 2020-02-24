from django.contrib import admin
from django.contrib.admin import ModelAdmin

from apps.staff.models import Team, SubTeam, Staff


@admin.register(Team)
class TeamAdmin(ModelAdmin):
    list_display = ['title_fa']
    pass


@admin.register(Staff)
class StaffAdmin(ModelAdmin):
    list_display = ['name_fa']


@admin.register(SubTeam)
class SubTeamAdmin(ModelAdmin):
    list_display = ['title_fa']
    pass
