# Generated by Django 2.2.9 on 2020-02-24 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0002_auto_20200224_1253'),
    ]

    operations = [
        migrations.AddField(
            model_name='subteam',
            name='order',
            field=models.IntegerField(default=0),
        ),
    ]
