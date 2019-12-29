from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Milestone


class UserHasParticipant(permissions.BasePermission):

    def has_permission(self, request, view):
        if not hasattr(request.user, 'participant'):
            Participant.objects.create(user=request.user)
        return True


class UserHasTeam(permissions.BasePermission):

    def has_object_permission(self, request, view):
        return len(request.user.participant.team.participants) == obj.team_size


class TeamParticipatedContest(permissions.BasePermission):

    # obj is a Contest instance which has 'teams' attr
    def has_object_permission(self, request, view, obj):
        return request.user.participant.team in obj.teams

