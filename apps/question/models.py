import enum
import os
import re
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models.signals import post_delete
from django.dispatch import receiver


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


class QuestionTag(models.Model):
    title = models.CharField(max_length=50)
    milestone = models.ForeignKey('contest.Milestone', related_name='question_tags', on_delete=models.CASCADE)

    def __str__(self):
        return self.title + str(self.id) + str(self.milestone)


class Question(PolymorphicModel):
    task = models.ForeignKey('contest.Task', related_name='questions', on_delete=None)

    judge_function = models.CharField(max_length=8000)
    judge_function_name = models.CharField(max_length=150, default='function')
    body = models.TextField()
    type = models.CharField(max_length=50, choices=QuestionTypes.TYPES)
    max_score = models.PositiveSmallIntegerField()
    tag = models.ForeignKey(QuestionTag, related_name='questions', on_delete=models.CASCADE, blank=True, null=True)

    @staticmethod
    def change_function_name(function: str):
        patt = 'def([^\(])+\(([^\)]+)\):'
        lines =  function.split('\n')
        first_line, other_lines = lines[0].strip(), lines[1:]
        if not re.match(patt, first_line):
            raise Exception('First line is not def folan')
        func_name = 'q_' + uuid.uuid4().hex[:16]
        search = re.search(patt, first_line)
        g = [search.group(i) for i in range(1, 3)]
        first_line = f'def {func_name}({g[1]}):'
        whole_lines = first_line + '\n' + '\n'.join(other_lines) + '\n'

        return whole_lines, func_name

    def clean(self):
        try:
            exec(self.judge_function.replace('_cwd', f'"{self.dir_path()}"'))
        except Exception as e:
            raise ValidationError(f'shitty judge function: {e}')

    def save(self, *args, **kwargs):
        self.judge_function = self.judge_function.replace('_cwd', f'"{self.dir_path()}"')
        super(Question, self).save(*args, **kwargs)

    def dir_path(self):
        return os.path.join(settings.MEDIA_ROOT, 'private', "question_" + str(self.id)) + '/'

    def __str__(self):
        return f'id:{self.id} task_topic:{self.task.topic}'


class NeededFilesForQuestionJudgment(models.Model):
    def upload_path(self, filename):
        return f'private/question_{self.question_id}/{filename}'

    question = models.ForeignKey(Question, related_name='files', on_delete=models.CASCADE)
    file = models.FileField(upload_to=upload_path, unique=True)

    def clean(self):
        print(settings.MEDIA_ROOT + self.upload_path(self.file.name.split('/')[-1]))
        if os.path.exists(settings.MEDIA_ROOT + self.upload_path(self.file.name.split('/')[-1])):
            raise ValidationError(f'File {self.file.name} already exists')


@receiver(post_delete, sender=NeededFilesForQuestionJudgment)
def submission_delete(sender, instance, **kwargs):
    instance.file.delete(False)


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
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class Selective(Question):
    pass


class SingleSelect(Selective):
    def pre_save(self):
        self.type = QuestionTypes.SINGLE_SELECT
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class MultiSelect(Selective):
    answer_count_limit = models.IntegerField()

    def pre_save(self):
        self.type = QuestionTypes.MULTI_SELECT
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class FileUpload(Question):
    file_size_limit = models.IntegerField()
    file_format = models.CharField(max_length=100)

    def pre_save(self):
        self.type = QuestionTypes.FILE_UPLOAD
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class ManualJudgment(Question):
    def pre_save(self):
        self.type = QuestionTypes.MANUAL_JUDGMENT
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

    def save(self, *args, **kwargs):
        self.pre_save()
        super().save(*args, **kwargs)


class NumericRange(Question):
    def pre_save(self):
        self.type = QuestionTypes.NUMERIC_RANGE
        self.judge_function, self.judge_function_name = Question.change_function_name(self.judge_function)

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

