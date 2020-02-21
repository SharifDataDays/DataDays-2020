from django.db import models

# Create your models here.

class Team(models.Model):
    title_en = models.CharField(max_length=50)
    title_fa = models.CharField(max_length=50)
    order = models.IntegerField()



class Staff(models.Model):
    team = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='staffs')

    image = models.ImageField()
    title_en = models.CharField(max_length=50)
    title_fa = models.CharField(max_length=50)
    name_en = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50)

