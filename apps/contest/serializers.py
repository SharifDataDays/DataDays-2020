from rest_framework.serializers import ModelSerializer

from apps.participation.serializers import TeamSerializer
from apps.question.serializers import QuestionSerializer
from apps.resources.serializers import DocumentSerializer

from . import models as contest_models


class MilestoneSerializer(ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Milestone
        fields = ['title', 'team_size', 'start_time', 'end_time']


class ContestSerializer(ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Contest
        fields = ['title', 'start_time', 'end_time', 'milestones']


class QuestionSubmissionSerializer(ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['question', 'answer', 'score']


class TrialSerializer(ModelSerializer):
    questions = QuestionSubmissionSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Trial
        fields = ['score', 'questions', 'due_time', 'start_time', 'submit_time']


class TaskSerializer(ModelSerializer):
    milestone = MilestoneSerializer()
    content = DocumentSerializer()

    class Meta:
        model = contest_models.Task
        fields = ['milestone', 'topic', 'trial_cooldown', 'content']


class TeamTaskSerializer(ModelSerializer):
    task = TaskSerializer()
    team = TeamSerializer()

    class Meta:
        model = contest_models.TeamTask
        fields = ['contest_finished', 'max_trials_count', 'last_trial_time', 'team', 'task']
