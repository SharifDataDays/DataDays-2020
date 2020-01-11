import ast
import os
import uuid

from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.conf import settings

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from . import models as question_models
from apps.question.models import QuestionTypes
from apps.question.permissions import HasStaffAccessToQuestions
from .serializers import QuestionPolymorphismSerializer, QuestionTestSerializer


class JudgeException(Exception):

    def __init__(self, *args, **kwargs):
        Exception.__init__(self, *args)


class QuestionsListAPIView(GenericAPIView):
    queryset = question_models.Question.objects.all()
    serializer_class = QuestionPolymorphismSerializer

    def get(self, request, question_type):
        query_set = self.get_questions_query_set(question_type)
        if query_set is None:
            raise Http404("Requested Questions Doesn't Exist")

        data = self.get_serializer(query_set, many=True).data
        return Response(data={'questions': data}, status=status.HTTP_200_OK)

    def get_questions_query_set(self, question_type):
        all_types = [question[0] for question in question_models.QuestionTypes.TYPES]
        if question_type == 'all':
            return self.get_queryset()
        if question_type in all_types:
            return self.get_queryset().filter(type=question_type)
        return None


class QuestionTestAPIView(GenericAPIView):
    queryset = question_models.Question.objects.all()
    permission_classes = (IsAuthenticated, HasStaffAccessToQuestions)
    serializer_class = QuestionTestSerializer

    def post(self, request):

        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            data = serializer.data
        question = question_models.Question.objects.get(id=data['question'])

        score = self.judge_question(question, data['answer'], data['file'])

        data['score'] = {
            'number': score.number,
            'status': score.status,
            'info': score.info
        }

        return Response(data, status=200)

    def judge_question(self, question, answer, file=None):
        from apps.contest.models import Score, ScoreStatusTypes

        answer = ast.literal_eval(answer.replace("'", '"'))
        score = Score()

        try:
            if question.type == QuestionTypes.MANUAL_JUDGMENT:
                score.number = 0.0
                score.status = ScoreStatusTypes.UNDEF
                score.info = "waiting for admin to score"

            exec(
                f'''\ndef get_path(filename):\n\treturn \'{question.dir_path()}\' + filename\n\n'''
                + question.judge_function
            )

            answer_name, answer = self.get_parameters(question.type, answer, file)

            if isinstance(answer, str):
                call_function = f'{question.judge_function_name}({answer_name}=\'{answer}\')'
            else:
                call_function = f'{question.judge_function_name}({answer_name}={answer})'
            score.number = eval(call_function) * question.max_score
            score.status = ScoreStatusTypes.SCORED
            score.info = "Judged Successfully"
        except JudgeException as e:
            score.status = ScoreStatusTypes.FAILED
            score.info = str(e)
        except Exception as e:
            score.status = ScoreStatusTypes.ERROR
            score.info = f'Judge function runtime error: {e}'

        return score

    def get_parameters(self, question_type, answer, file=None):
        if question_type in [QuestionTypes.SINGLE_ANSWER, QuestionTypes.SINGLE_SELECT]:
            return 'answer', answer[0]
        elif question_type in [QuestionTypes.MULTI_ANSWER, QuestionTypes.MULTI_SELECT]:
            return 'answers', answer
        elif question_type == QuestionTypes.NUMERIC_RANGE:
            return 'range', answer
        elif question_type == QuestionTypes.FILE_UPLOAD:
            dirname = f'{settings.MEDIA_ROOT}question_tests'
            os.makedirs(dirname, exist_ok=True)
            filename = f'{dirname}/t_{uuid.uuid4().hex[:16]}'
            with open(filename, 'w+') as f:
                [f.write(line) for line in f]
                f.close()
            return 'file_path', filename

