from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Milestone


class UserParticipatedTeam(permissions.BasePermission):

    def has_permission(self, request, view):
        if hasattr(request.user, 'participant') \
                and request.user.participant is not None \
                and hassattr(request.user.participant, 'team') \
                and request.user.participant.team is not None:
            return True
        return False


class CompletedTeam(permission.BasePermission):

    # obj is a Contest instance which has 'team_size' attr
    def has_object_permission(self, request, view, obj):
        return len(request.user.participant.team.participants) == obj.team_size


class TeamParticipatedContest(permissions.BasePermission):

    # obj is a Contest instance which has 'teams' attr
    def has_object_permission(self, request, view, obj):
        return request.user.participant.team in obj.teams

