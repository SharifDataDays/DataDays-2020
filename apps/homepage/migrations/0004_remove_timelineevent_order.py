# Generated by Django 2.2.8 on 2019-12-27 12:59

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0003_auto_20191226_1553'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='timelineevent',
            name='order',
        ),
    ]
