from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Contest, Milestone, TeamTask


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

        return obj in [team.contest for team in request.user.participant.teams.all()]


class UserHasTeamTasks(permissions.BasePermission):

    # obj is Milestone instance
    def has_object_permission(self, request, view, obj):
        if not isinstance(obj, Milestone):
            return True

        if not obj.released:
            if request.user.is_staff:
                return True
            return False

        team = request.user.participant.teams.get(contest=obj.contest)
        team_tasks = team.tasks.all()
        for task in obj.tasks.all():
            if task not in [tt.task for tt in team_tasks]:
                TeamTask.objects.create(team=team, task=task, content_finished=False)
        return True
