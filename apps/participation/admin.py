from django.contrib import admin

from apps.contest.admin import TeamTaskInline
from . import models as participation_models


# Register your models here.


class ParticipantInline(admin.StackedInline):
    model = participation_models.Participant


class InvitationInline(admin.TabularInline):
    model = participation_models.Invitation
    fk_name = 'participant'


@admin.register(participation_models.Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['id', 'get_username', 'get_fullname']
    list_display_links = ['id', 'get_username', 'get_fullname']
    search_fields = ['get_username', 'get_fullname']
    sortable_by = ['get_username', 'get_fullname']

    def get_username(self, participant: participation_models.Participant):
        return participant.user.username

    get_username.short_description = 'User username'
    get_username.admin_order_field = 'user_username'

    def get_fullname(self, participant: participation_models.Participant):
        return participant.user.get_full_name()

    get_fullname.short_description = 'User fullname'
    get_fullname.admin_order_field = 'user_fullname'

    inlines = [InvitationInline]


@admin.register(participation_models.Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ['name', 'team_participants', 'team_badges', 'finalized']
    inlines = [TeamTaskInline]

    def team_participants(self, obj):
        return ', '.join((p.user.username for p in obj.participants.all()))

    def team_badges(self, obj):
        return ', '.join((b.text for b in obj.badges.all()))


@admin.register(participation_models.Invitation)
class InvitationAdmin(admin.ModelAdmin):
    pass
