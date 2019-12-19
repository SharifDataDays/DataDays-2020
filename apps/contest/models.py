from django.db import models
from django.contrib.auth.models import User

from ..question.models import QuestionTypes, Question


# Create your models here.


class Contest(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    title = models.CharField(max_length=100)


class Milestone(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    contest = models.ForeignKey(Contest, related_name='milestones', on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    team_size = models.PositiveSmallIntegerField()


class Task(models.Model):
    user = models.ForeignKey(User, related_name='trials', on_delete=models.CASCADE)
    milestone = models.ForeignKey(Milestone, related_name='tasks', on_delete=models.CASCADE)
    topic = models.CharField(max_length=200, unique=True)
    content = models.TextField()


class Team(models.Model):
    milestone = models.ForeignKey(Milestone, related_name='teams', on_delete=models.CASCADE)


class TeamTask(models.Model):
    task = models.ForeignKey(Task, related_name='team_tasks', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='tasks', on_delete=models.CASCADE)
    content_finished = models.BooleanField(default=False)
    max_trials_count = models.PositiveSmallIntegerField(default=3)
    last_trial_time = models.DateTimeField(null=True, blank=True)


class Participant(models.Model):
    user = models.OneToOneField(User, related_name='participant', on_delete=models.CASCADE)
    team = models.ForeignKey(Team, related_name='participants', on_delete=models.CASCADE)


class Trial(models.Model):
    task = models.ForeignKey(Task, related_name='trials', on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField(default=0)
    due_time = models.DateTimeField()
    start_time = models.DateTimeField(auto_now_add=True)
    submit_time = models.DateTimeField(null=True, blank=True)


class TrialRecipe(models.Model):
    task = models.OneToOneField(Task, related_name='trial_recipe', on_delete=models.CASCADE)


class QuestionRecipe(models.Model):
    trial_recipe = models.ForeignKey(TrialRecipe, related_name='question_recipes', on_delete=models.CASCADE)
    question_type = models.CharField(max_length=20, choices=QuestionTypes.TYPES)
    priority = models.PositiveSmallIntegerField()
    count = models.PositiveSmallIntegerField()


class UserAnswer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='answers', on_delete=models.CASCADE)
    trial = models.ForeignKey(Trial, related_name='user_answers', on_delete=models.CASCADE)
    selections = models.CharField(max_length=100, blank=True, null=False)
    text = models.CharField(max_length=2000, blank=True, null=False)
    file = models.FileField(null=True, blank=True)


class TrialQuestion(models.Model):
    trial = models.ForeignKey(Trial, related_name='questions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='trial_questions', on_delete=models.CASCADE)


class QuestionSubmission(models.Model):
    trial = models.ForeignKey(Trial, related_name='question_submissions', on_delete=models.CASCADE)
    question = models.ForeignKey(Question, related_name='question_submission', on_delete=models.CASCADE)
    answer = models.TextField()
    score = models.PositiveSmallIntegerField(default=0)
