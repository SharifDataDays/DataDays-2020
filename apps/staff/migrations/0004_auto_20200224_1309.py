# Generated by Django 2.2.9 on 2020-02-24 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('staff', '0003_auto_20200224_1300'),
    ]

    operations = [
        migrations.AddField(
            model_name='staff',
            name='description',
            field=models.TextField(default='', max_length=400),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='staff',
            name='link',
            field=models.URLField(default='', max_length=400),
            preserve_default=False,
        ),
    ]
