from django.contrib.auth.models import User
from django.db import models

# Create your models here.
from apps.contest.models import Milestone


class Team(models.Model):
    milestone = models.ForeignKey(Milestone, related_name='teams', on_delete=models.CASCADE)

    def __str__(self):
        return self.id


class Participant(models.Model):
    user = models.OneToOneField(User, related_name='participant', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='participants', on_delete=models.CASCADE)

    def __str__(self):
        return self.user.username


class Invitation(models.Model):
    host = models.ForeignKey(Participant, related_name='invitations', on_delete=models.CASCADE)
    guest = models.ForeignKey(Participant, related_name='invitations', on_delete=models.CASCADE)

    def __str__(self):
        return self.id
