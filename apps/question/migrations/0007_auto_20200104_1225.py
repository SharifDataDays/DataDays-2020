# Generated by Django 2.2.8 on 2020-01-04 12:25

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('contest', '0012_auto_20200103_1556'),
        ('question', '0006_auto_20191227_1513'),
    ]

    operations = [
        migrations.CreateModel(
            name='QuestionTag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=50)),
                ('milestone', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='question_tags', to='contest.Milestone')),
            ],
        ),
        migrations.AddField(
            model_name='question',
            name='tag',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='questions', to='question.QuestionTag'),
        ),
    ]
