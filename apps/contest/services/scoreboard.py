from apps.contest.models import TeamTask
from apps.participation.models import Team


class Scoreboard:
    def __init__(self, in_contest):
        self.contest = []
        self.milestones = {
            milestone.id: {
                'table': [
                    {
                        'team': team.name,
                        'total': 0,
                        'scores': {
                            task.id: task.score for task in
                            TeamTask.objects.filter(team=team, task__milestone=milestone)
                        }
                    } for team in Team.objects.filter(contest=milestone.contest)
                ]
            } for milestone in in_contest.milestones
        }

    def update(self, team_task):
        for team in self.milestones[team_task.task.milestone.id]['table']:
            if team.name == team_task.team.name:
                team['total'] -= team['scores'][team_task.task.id]
                team['scores'][team_task.task.id] = team_task.score
                team['total'] += team_task.score

