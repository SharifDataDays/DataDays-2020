# Generated by Django 2.2.9 on 2020-02-11 00:17

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0025_task_order'),
    ]

    operations = [
        migrations.AddField(
            model_name='contest',
            name='description',
            field=models.TextField(null=True),
        ),
        migrations.AddField(
            model_name='contest',
            name='rules',
            field=models.TextField(null=True),
        ),
    ]
