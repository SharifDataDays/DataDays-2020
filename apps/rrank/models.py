import secrets

from django.db import models

from apps.participation.models import Team


class TeamNum(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    number = models.IntegerField()

    def __str__(self):
        return f'{self.team}: {self.number}'


class TeamToken(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE)
    token = models.CharField(max_length=128, blank=True)

    def save(self, *args, **kwargs):
        self.token = secrets.token_urlsafe(64)
        super().save(*args, **kwargs)

    def __str__(self):
        return f'{self.team}: {self.token}'
