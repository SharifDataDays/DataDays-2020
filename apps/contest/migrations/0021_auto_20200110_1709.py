# Generated by Django 2.2.8 on 2020-01-10 17:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0020_auto_20200110_1550'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='released',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='milestone',
            name='released',
            field=models.BooleanField(default=False),
        ),
    ]