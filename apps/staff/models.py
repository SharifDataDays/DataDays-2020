from django.db import models


class Team(models.Model):
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.title_fa)


class SubTeam(models.Model):
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50)
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='subteams',null=True)
    order = models.IntegerField(default=0)

    def __str__(self):
        return '%s' % (self.title_fa)


class Staff(models.Model):
    subteam = models.ForeignKey(
        SubTeam, on_delete=models.CASCADE, related_name='staffs')

    image = models.ImageField()
    title_en = models.CharField(max_length=50, blank=True)
    title_fa = models.CharField(max_length=50)
    name_en = models.CharField(max_length=50, blank=True)
    name_fa = models.CharField(max_length=50)
    order = models.IntegerField(default=1, blank=True)

    def __str__(self):
        return '%s' % (self.name_fa)
