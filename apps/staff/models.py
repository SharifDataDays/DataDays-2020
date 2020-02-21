from django.db import models

# Create your models here.

class Team(models.Model):
    title_en = models.CharField(max_length=50)
    title_fa = models.CharField(max_length=50)



class Staff(models.Model):
    post = models.ForeignKey(
        Team, on_delete=models.CASCADE, related_name='staffs')

    image = models.ImageField()
    description_en = models.TextField(max_length=300)
    description_fa = models.TextField(max_length=300)
    name_en = models.CharField(max_length=50)
    name_fa = models.CharField(max_length=50)

