from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Team(models.Model):
    contest = models.ForeignKey('contest.Contest', related_name='teams', on_delete=models.CASCADE)
    badges = models.ManyToManyField('participation.Badge', related_name='teams', null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)

    @staticmethod
    def get_team(participant, contest):
        if contest not in [team.contest for team in participant.teams.all()]:
            new_team = Team.objects.create(contest=contest, name=participant.user.username)
            participant.teams.add(new_team)
        return participant.teams.get(contest=contest)

    def __str__(self):
        return self.name


class Participant(models.Model):
    user = models.OneToOneField(User, related_name='participant', on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, related_name='participants')

    def __str__(self):
        return self.user.username


class Invitation(models.Model):
    host = models.ForeignKey(Participant, related_name='invitations_as_host', on_delete=models.CASCADE)
    guest = models.ForeignKey(Participant, related_name='invitations_as_gust', on_delete=models.CASCADE)

    @staticmethod
    def get_participant(user):
        if not hasattr(user, 'participant'):
            Participant.objects.create(user=user)
        return user.participant

    def __str__(self):
        return str(self.id)


class Badge(models.Model):
    image = models.ImageField()
    milestone = models.ForeignKey('contest.Milestone', related_name='badges', on_delete=models.CASCADE)
    text = models.TextField()

    def __str__(self):
        return f'id:{self.id} milestone_title:{self.milestone.title}'
