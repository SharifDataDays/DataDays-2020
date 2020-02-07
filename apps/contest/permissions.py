from rest_framework import permissions

from apps.participation.models import Team, Participant
from apps.contest.models import Contest, Milestone, TeamTask


class UserHasTeam(permissions.BasePermission):

    def has_permission(self, request, view):
        if not hasattr(request.user, 'participant'):
            Participant.objects.create(user=request.user)

        contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        if contest.count() == 0:
            return False
        contest = contest.get()

        if request.user.participant.teams.filter(contest=contest).count() == 0:
            Team.get_team(request.user.participant, contest)

        if not contest.released:
            if request.user.is_staff:
                return True
            return False

        return True

class UserHasTeamTasks(permissions.BasePermission):

    def has_permission(self, request, view):
        milestone = Milestone.objects.filter(id=view.kwargs['milestone_id'])
        if milestone.count() == 0:
            return False
        milestone = milestone.get()

        if not milestone.released:
            if request.user.is_staff:
                return True
            return False

        team = request.user.participant.teams.get(contest=milestone.contest)
        team_tasks = team.tasks.all()
        for task in milestone.tasks.all():
            if task not in [tt.task for tt in team_tasks]:
                TeamTask.objects.create(team=team, task=task, content_finished=False)
        return True


class ProfileCompleted(permissions.BasePermission):

    message = """
        complete your profile first
    """

    def has_permission(self, request, view):
        return request.user.profile.completed()


class TeamFinalized(permissions.BasePermission):

    message = """
        complete your team for this contest first
    """

    def has_permission(self, request, view):
        contest = Contest.objects.filter(id=view.kwargs['contest_id'])
        if contest.count() == 0:
            return False
        contest = contest.get()

        if contest.team_size == 1:
            return True

        return obj.finalized()

