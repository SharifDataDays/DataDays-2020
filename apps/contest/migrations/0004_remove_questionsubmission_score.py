# Generated by Django 2.2.8 on 2019-12-27 15:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0003_auto_20191226_2257'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='questionsubmission',
            name='score',
        ),
    ]
