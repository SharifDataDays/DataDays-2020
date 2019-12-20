from django.shortcuts import render
from django.http import Http404

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from . import models as question_models
from .serializers import QuestionPolymorphismSerializer


# Create your views here.

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
