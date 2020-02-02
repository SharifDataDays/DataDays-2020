from django.contrib.auth.models import User
from django.db import models
from django.dispatch import receiver
from django.db.models.signals import pre_delete


# Create your models here.


class Team(models.Model):
    contest = models.ForeignKey('contest.Contest', related_name='teams', on_delete=models.CASCADE)
    badges = models.ManyToManyField('participation.Badge', related_name='teams', null=True, blank=True)
    name = models.CharField(max_length=50, unique=True)

    name_finalized = models.BooleanField(default=False)

    @staticmethod
    def get_team(participant, contest):
        if contest not in [team.contest for team in participant.teams.all()]:
            new_team = Team.objects.create(contest=contest, name=participant.user.username)
            participant.teams.add(new_team)
        return participant.teams.get(contest=contest)

    def finalized(self):
        return self.name_finalized and self.participants.count() == self.contest.team_size

    def __str__(self):
        return self.name


class Participant(models.Model):
    user = models.OneToOneField(User, related_name='participant', on_delete=models.CASCADE)
    teams = models.ManyToManyField(Team, related_name='participants')

    def __str__(self):
        return self.user.username


@receiver(pre_delete, sender=Participant, dispatch_uid='participant_delete_signal')
def delete_teams(sender, instance, *args, **kwargs):
    instance.teams.all().delete()


class Invitation(models.Model):
    contest = models.ForeignKey('contest.Contest',
            related_name='invitations', on_delete=models.CASCADE)

    team = models.ForeignKey(Team,
            related_name='invitations', on_delete=models.CASCADE)
    participant = models.ForeignKey(Participant,
            related_name='invitations', on_delete=models.CASCADE)

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
