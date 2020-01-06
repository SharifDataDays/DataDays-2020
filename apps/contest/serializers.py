from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from apps.participation.serializers import TeamSerializer
from apps.question.serializers import QuestionPolymorphismSerializer
from apps.resources.serializers import DocumentSerializer

from . import models as contest_models


class TaskSerializer(ModelSerializer):
    content = DocumentSerializer()

    class Meta:
        model = contest_models.Task
        fields = ['id', 'topic', 'trial_cooldown', 'content', 'scoring_type']


class MilestoneSerializer(ModelSerializer):
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = contest_models.Milestone
        fields = ['id', 'title', 'start_time', 'end_time', 'tasks']


class ContestSerializer(ModelSerializer):
    milestones = serializers.PrimaryKeyRelatedField(many=True, read_only=True)

    class Meta:
        model = contest_models.Contest
        fields = ['id', 'title', 'team_size', 'start_time', 'end_time', 'milestones']


class ContestAsAListItemSerializer(ModelSerializer):
    class Meta:
        model = contest_models.Contest
        fields = ['id', 'title', 'start_time', 'end_time']


class ScoreSerializer(ModelSerializer):
    class Meta:
        model = contest_models.Score
        fields = ['question_submission_id', 'number', 'status', 'info']


class QuestionSubmissionSerializer(ModelSerializer):
    question = QuestionPolymorphismSerializer()
    score = ScoreSerializer()

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['id', 'question', 'answer', 'file_answer', 'score']


class QuestionSubmissionPostSerializer(ModelSerializer):
    id = serializers.ModelField(model_field=contest_models.QuestionSubmission()._meta.get_field('id'))
    score = ScoreSerializer(read_only=True)
    file = serializers.FileField(required=False)

    class Meta:
        model = contest_models.QuestionSubmission
        fields = ['id', 'answer', 'score', 'file']


class TrialSerializer(ModelSerializer):
    question_submissions = QuestionSubmissionSerializer(many=True, read_only=True)
    score = ScoreSerializer()

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'score', 'question_submissions', 'due_time', 'start_time', 'submit_time']


class TrialPostSerializer(ModelSerializer):
    id = serializers.ModelField(model_field=contest_models.Trial()._meta.get_field('id'))
    question_submissions = QuestionSubmissionPostSerializer(many=True)
    final_submit = serializers.BooleanField(default=False)
    score = serializers.FloatField(read_only=True)

    class Meta:
        model = contest_models.Trial
        fields = ['id', 'question_submissions', 'final_submit', 'score']

    def save(self):
        tf = contest_models.Trial.objects.filter(id=self.validated_data['id'])
        if tf.count() != 1:
            raise Exception
        trial = tf.get()
        qss = trial.question_submissions.all()
        for qs in self.validated_data['question_submissions']:
            qsf = qss.filter(id=qs['id'])
            if qsf.count() != 1:
                raise Exception
            q = qsf.get()
            q.answer = qs['answer']
            q.save()


class TeamTaskSerializer(ModelSerializer):
    task = TaskSerializer()
    team = TeamSerializer()

    class Meta:
        model = contest_models.TeamTask
        fields = ['id', 'contest_finished', 'max_trials_count', 'last_trial_time', 'team', 'task']
