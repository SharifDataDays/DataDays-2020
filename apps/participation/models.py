from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Team(models.Model):
    contest = models.ForeignKey('contest.Contest', related_name='teams', on_delete=models.CASCADE)
    badges = models.ManyToManyField('participation.Badge', related_name='teams', null=True, blank=True)
    name = models.CharField(max_length=50)

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

    def __str__(self):
        return str(self.id)


class Badge(models.Model):
    image = models.ImageField()
    milestone = models.ForeignKey('contest.Milestone', related_name='badges', on_delete=models.CASCADE)
    text = models.TextField()
