# Generated by Django 2.2.8 on 2020-01-31 19:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blog', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='shown',
            field=models.BooleanField(default=True),
        ),
    ]
