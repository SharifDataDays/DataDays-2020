# Generated by Django 2.2.9 on 2020-02-20 18:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0008_timer'),
    ]

    operations = [
        migrations.AddField(
            model_name='count',
            name='query',
            field=models.CharField(default='', max_length=400),
            preserve_default=False,
        ),
    ]
