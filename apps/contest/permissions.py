from rest_framework import permissions

from apps.participation.models import Team
from apps.contest.models import Milestone

class TeamParticipatedMilestone(permissions.BasePermission):

    # obj is a Contest instance which has 'teams' attr
    def has_object_permission(self, request, view, obj):
        return request.user.participant.team in obj.teams

