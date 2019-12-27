from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.participation.serializers import TeamSerializer
from apps.question.serializers import QuestionSerializer
from apps.resources.serializers import DocumentSerializer

from . import models as contest_models


class TaskSerializer(ModelSerializer):
    content = DocumentSerializer()

    class Meta:
        model = contest_models.Task
        fields = ['id', 'topic', 'trial_cooldown', 'content']


class MilestoneSerializer(ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Milestone
        fields = ['id', 'title', 'start_time', 'end_time', 'tasks']


class ContestSerializer(ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Contest
        fields = ['id', 'title', 'team_size', 'start_time', 'end_time', 'milestones']


class ScoreSerializer(ModelSerializer):

    class Meta:
        model = contest_models.Score
        fields = '__all__'


class QuestionSubmissionSerializer(ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['id', 'question', 'answer', 'score']


class QuestionSubmissionPostSerializer(ModelSerializer):

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['question', 'answer']


class TrialSerializer(ModelSerializer):
    question_submissions = QuestionSubmissionSerializer(many=True, read_only=True)
    score = ScoreSerializer()

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'score', 'question_submissions', 'due_time', 'start_time', 'submit_time']


class TrialPostSerializer(ModelSerializer):

    question_submissions = QuestionSubmissionPostSerializer(many=True)
    final_submit = serializers.BooleanField(default=False)

    class Meta:
        model = contest_models.Trial
        fields = ['question_submissions', 'final_submit']

class TeamTaskSerializer(ModelSerializer):
    task = TaskSerializer()
    team = TeamSerializer()

    class Meta:
        model = contest_models.TeamTask
        fields = ['id', 'contest_finished', 'max_trials_count', 'last_trial_time', 'team', 'task']


