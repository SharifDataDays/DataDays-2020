from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django.db import models


class University(models.Model):
    name = models.CharField(max_length=200, unique=True)

    def __str__(self):
        return self.name


class Profile(models.Model):
    user = models.OneToOneField(User,
                                on_delete=models.CASCADE,
                                related_name='profile'
                                )
    firstname_fa = models.TextField(max_length=30)
    firstname_en = models.TextField(max_length=30)
    lastname_fa = models.TextField(max_length=30)
    lastname_en = models.TextField(max_length=30)
    birth_date = models.DateField()
    university = models.CharField(max_length=50, null=True)

    uni = models.ForeignKey(University, on_delete=models.CASCADE, null=True)
    major = models.CharField(max_length=100, null=True)
    bmp = models.CharField(
            max_length=50,
            choices=(
                ('BAC', 'Bacholar'),
                ('MAS', 'Master'),
                ('PHD', 'Ph.D'),
            ),
            null=True
        )
    student_id = models.IntegerField(null=True)
    phone_regex = RegexValidator(regex=r'^0\d{10}$', message=(
        "Phone number must be entered in the format: '09001234567'."
        " Up to 15 digits allowed."
    ))
    phone_number = models.CharField(validators=[phone_regex], max_length=15, null=True)

    def completed(self):
        return self.uni is not None and self.major is not None and self.bmp is not None

    def __str__(self):
        return f'username: {self.user.username},' \
            f'name: {self.firstname_en} {self.lastname_en},' \
            f'email: {self.user.email}'


class ResetPasswordToken(models.Model):
    uid = models.CharField(max_length=100)
    token = models.CharField(max_length=100)
    expiration_date = models.DateTimeField()


class ActivateUserToken(models.Model):
    token = models.CharField(max_length=100)
    eid = models.CharField(max_length=100, null=True)

