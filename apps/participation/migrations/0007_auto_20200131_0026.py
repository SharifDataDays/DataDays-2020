# Generated by Django 2.2.8 on 2020-01-31 00:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('participation', '0006_auto_20200131_0025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='invitation',
            name='contest',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='invitations', to='contest.Contest'),
            preserve_default=False,
        ),
    ]
