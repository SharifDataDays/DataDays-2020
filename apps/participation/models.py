from django.contrib.auth.models import User
from django.db import models


# Create your models here.


class Team(models.Model):
    contest = models.ForeignKey('contest.Contest', related_name='teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Participant(models.Model):
    user = models.OneToOneField(User, related_name='participant', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='participants', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Invitation(models.Model):
    host = models.ForeignKey(Participant, related_name='invitations_as_host', on_delete=models.CASCADE)
    guest = models.ForeignKey(Participant, related_name='invitations_as_gust', on_delete=models.CASCADE)

    def __str__(self):
        return self.id
