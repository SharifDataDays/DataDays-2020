import secrets

from django.db import models

from apps.participation.models import Team


class TeamNum(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    number = models.IntegerField()


class TeamToken(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        self.token = secrets.token_urlsafe(64)
        super().save(*args, **kwargs)
