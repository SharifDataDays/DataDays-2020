import enum
import os
import re
import uuid

from django.conf import settings
from django.db import models
from polymorphic.models import PolymorphicModel


# Create your models here.

class AnswerDataTypes:
    INTEGER = 'int'
    DOUBLE = 'double'
    TEXT = 'text'
    TYPES = (
        (INTEGER, 'integer'),
        (DOUBLE, 'double'),
        (TEXT, 'text'),
    )


class QuestionTypes:
    SINGLE_ANSWER = 'single_answer'
    MULTI_ANSWER = 'multi_answer'
    SINGLE_SELECT = 'single_select'
    MULTI_SELECT = 'multi_select'
    FILE_UPLOAD = 'file_upload'
    MANUAL_JUDGMENT = 'manual_judgment'
    NUMERIC_RANGE = 'numeric_range'
    TYPES = (
        (SINGLE_ANSWER, 'Single Answer'),
        (MULTI_ANSWER, 'Multi Answer'),
        (SINGLE_SELECT, 'Single Select'),
        (MULTI_SELECT, 'Multi Select'),
        (FILE_UPLOAD, 'File Upload'),
        (MANUAL_JUDGMENT, 'Manual Judgment'),
        (NUMERIC_RANGE, 'Numeric Range'),
    )


class Question(PolymorphicModel):
    task = models.ForeignKey('contest.Task', related_name='questions', on_delete=None)

    judge_function = models.CharField(max_length=8000)
    judge_function_name = models.CharField(max_length=150, default='function')
    body = models.TextField()
    type = models.CharField(max_length=50, choices=QuestionTypes.TYPES)
    max_score = models.PositiveSmallIntegerField()

    @staticmethod
    def change_function_name(function: str):
        name_start = function.find(" ")
        while function[name_start] == " ":
            name_start += 1
        name_end = function.find("(")
        function_new_name = uuid.uuid4().hex[:16]
        return function[:name_start] + function_new_name + function[name_end:], function_new_name

    def dir_path(self):
        return settings.MEDIA_ROOT + 'private/' + str(self.id)

    def __str__(self):
        return "id: " + str(self.id) + " task: " + str(self.task.topic)


class NeededFilesForQuestionJudgment(models.Model):
    def upload_path(instance, filename):
        return os.path.join('private/', str(instance.question_id), filename)

    question = models.ForeignKey(Question, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path, unique=True)


class SingleAnswer(Question):
    answer_type = models.CharField(max_length=30, choices=AnswerDataTypes.TYPES)

    def pre_save(self):
        self.type = QuestionTypes.SINGLE_ANSWER
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class MultiAnswer(Question):
    answer_count_limit = models.IntegerField()
    answer_type = models.CharField(max_length=30, choices=AnswerDataTypes.TYPES)

    def pre_save(self):
        self.type = QuestionTypes.MULTI_ANSWER

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class Selective(Question):
    pass


class SingleSelect(Selective):
    def pre_save(self):
        self.type = QuestionTypes.SINGLE_SELECT

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class MultiSelect(Selective):
    answer_count_limit = models.IntegerField()

    def pre_save(self):
        self.type = QuestionTypes.MULTI_SELECT

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class FileUpload(Question):
    file_size_limit = models.IntegerField()
    file_format = models.CharField(max_length=100)

    def pre_save(self):
        self.type = QuestionTypes.FILE_UPLOAD

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class ManualJudgment(Question):
    def pre_save(self):
        self.type = QuestionTypes.MANUAL_JUDGMENT

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class NumericRange(Question):
    def pre_save(self):
        self.type = QuestionTypes.NUMERIC_RANGE

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class Choices(models.Model):
    body = models.TextField(max_length=500)
    label = models.CharField(max_length=5)
    selective_question = models.ForeignKey(Selective, related_name='choices', on_delete=models.CASCADE)

    def __str__(self):
        return "Label: " + str(self.label) + " Question_id: " + str(
            self.selective_question.id) + " Question_Topic: " + str(
            self.selective_question.task.topic) + " "
