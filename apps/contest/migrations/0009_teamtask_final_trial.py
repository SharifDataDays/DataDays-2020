# Generated by Django 2.2.8 on 2019-12-28 09:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0008_auto_20191227_2006'),
    ]

    operations = [
        migrations.AddField(
            model_name='teamtask',
            name='final_trial',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='contest.Trial'),
        ),
    ]