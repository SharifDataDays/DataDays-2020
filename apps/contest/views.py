import json

from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from datadays.apps.contest.Exceptions.trial_validation_exception import TrialNotAllowed
from . import models as contest_models, serializers
from .services import trial_maker


class CreateTrialAPIView(GenericAPIView):
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TrialSerializer

    def get(self, request):
        data = json.loads(request.body)
        task = get_object_or_404(contest_models.Trial, topic=data.get('topic'), user__username=data.get('username'))
        try:
            trial = trial_maker.TrialMaker(task)()
        except TrialNotAllowed as e:
            return Response(data={'error': str(e)}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = self.get_serializer(trial).data
        return Response(data={'trial': data}, status=status.HTTP_200_OK)


class SubmitTrialAPIView(GenericAPIView):
    pass


class UserTasksListAPIView(GenericAPIView):
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    def get(self, request, username):
        tasks = self.get_queryset().filter(user__username=username)
        data = self.get_serializer(tasks, many=True).data
        return Response(data={'user': username, 'tasks': data}, status=status.HTTP_200_OK)
