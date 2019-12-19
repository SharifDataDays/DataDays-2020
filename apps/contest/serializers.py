from rest_framework.serializers import ModelSerializer

from apps.question.serializers import QuestionSerializer
from . import models as contest_models


class MilestoneSerializer(ModelSerializer):
    class Meta:
        model = contest_models.Milestone
        fields = ['title']


class ContestSerializer(ModelSerializer):
    milestones = MilestoneSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Contest
        fields = ['title', 'milestones']


class TrialQuestionSerializer(ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = contest_models.TrialQuestion
        fields = ['question']


class TrialSerializer(ModelSerializer):
    questions = TrialQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Trial
        fields = ['score', 'questions', 'due_time', 'start_time', 'submit_time']


class TaskSerializer(ModelSerializer):
    milestone = MilestoneSerializer()

    class Meta:
        model = contest_models.Task
        fields = ['milestone', 'topic', 'content_finished', 'trails_count', 'last_trial_time', 'content']


class UserAnswerSerializer(ModelSerializer):
    question = QuestionSerializer()

    class Meta:
        model = contest_models.UserAnswer
        fields = ['question', 'selections', 'text']
