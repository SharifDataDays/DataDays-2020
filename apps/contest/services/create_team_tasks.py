from typing import List, Union

from apps.contest.models import Milestone, TeamTask
from apps.participation.models import Team


class GetOrCreateTeamTasks:

    def __init__(self, team: Team, milestone: Milestone):
        self.milestone = milestone
        self.team = team
        self.team_tasks: Union[List[TeamTask], None] = None

    def get_team_tasks(self):
        if not self._get_existing_team_tasks():
            self._create_team_tasks()
        return self.team_tasks

    def _create_team_tasks(self):
        team_tasks = []
        for task in self.milestone.tasks:
            team_tasks.append(TeamTask(task=task, team=self.team, content_finished=0))
        TeamTask.objects.bulk_create(team_tasks)
        self.team_tasks = team_tasks

    def _get_existing_team_tasks(self):
        team_tasks = TeamTask.objects.filter(team=self.team).filter(task__milestone=self.milestone)
        if list(team_tasks):
            self.team_tasks = team_tasks
            return True
        return False
