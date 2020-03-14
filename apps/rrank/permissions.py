from rest_framework import permissions

from apps.rrank.models import TeamToken


class TeamBelongsToUser(permissions.BasePermission):

    message = "Team doesn't belong to user"

    def has_permission(self, request, view):
        try:
            tt = TeamToken.objects.filter(token=view.kwargs['token'])
        except KeyError:
            return True

        if tt.count() == 0:
            return False
        tt = tt.get()

        return tt.team in request.user.participant.teams.all()
