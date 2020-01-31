from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Contest


class UserHasParticipant(permissions.BasePermission):

    def has_permission(self, request, view):
        if not hasattr(request.user, 'participant'):
            Participant.objects.create(user=request.user)
        return True


class UserHasTeamInContest(permissions.BasePermission):

    # obj is Contest instance
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Contest):
            return True

        if not obj.released:
            if request.user.is_staff:
                return True
            return False

        has_team = obj in [team.contest for team in request.user.participant.teams.all()]
        if not has_team:
            team = Team.objects.create(contest=obj, name=f'{request.user.username}_{obj.id}')
            request.user.participant.teams.add(team)
        return True

