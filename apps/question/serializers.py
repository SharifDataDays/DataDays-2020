from rest_framework import serializers
from rest_polymorphic.serializers import PolymorphicSerializer

from apps.contest.serializers import TaskSerializer
from . import models as question_models


class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = question_models.Choices
        fields = ['body', 'label']


class QuestionSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.Question
        fields = ['id', 'task', 'max_score', 'body', 'type']


class SingleAnswerSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.SingleAnswer
        fields = ['id', 'task', 'max_score', 'body', 'type', 'answer_type']


class MultiAnswerSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.MultiAnswer
        fields = ['id', 'task', 'max_score', 'body', 'type', 'answer_count_limit', 'answer_type']


class SingleSelectSerializers(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    task = TaskSerializer()

    class Meta:
        model = question_models.SingleSelect

        fields = ['id', 'task', 'max_score', 'body', 'type', 'choices']


class MultiSelectSerializer(serializers.ModelSerializer):
    choices = ChoiceSerializer(many=True, read_only=True)
    task = TaskSerializer()

    class Meta:
        model = question_models.MultiSelect

        fields = ['id', 'task', 'max_score', 'body', 'type', 'choices']


class FileUploadSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.FileUpload

        fields = ['id', 'task', 'max_score', 'body', 'type', 'file_size_limit', 'file_format']


class ManualJudgmentSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.ManualJudgment

        fields = ['id', 'task', 'max_score', 'body', 'type']


class NumericRangeSerializer(serializers.ModelSerializer):
    task = TaskSerializer()

    class Meta:
        model = question_models.NumericRange

        fields = ['id', 'task', 'max_score', 'body', 'type']


class QuestionPolymorphismSerializer(PolymorphicSerializer):
    model_serializer_mapping = {
        question_models.Question: QuestionSerializer,
        question_models.SingleAnswer: SingleAnswerSerializer,
        question_models.MultiAnswer: MultiAnswerSerializer,
        question_models.SingleSelect: SingleSelectSerializers,
        question_models.MultiSelect: MultiSelectSerializer,
        question_models.FileUpload: FileUploadSerializer,
        question_models.ManualJudgment: ManualJudgmentSerializer,
        question_models.NumericRange: NumericRangeSerializer
    }
