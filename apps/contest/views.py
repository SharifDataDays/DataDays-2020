import json

from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.contest.Exceptions.trial_validation_exception import TrialNotAllowed
from apss.contest.premissions import TeamParticipatedContest
from . import models as contest_models, serializers
from .services import trial_maker


class ContestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ContestSerializer

    def get(self, request, contest_id):
        contest = get_object_or_404(contest_models.Contest, pk=contest_id)
        if request.user.participant is None:
            new_team = Team(contest=contest, name=request.user.username)
            new_team.save()
            new_participant = Participant(user=request.user, team=new_team)
            new_participant.save()
        data = self.get_serializer(contest).data
        return Response(data)


class MilestoneAPIView(GenericAPIView):
    queryset = contest_models.Milestone.objcets.all()
    serializer_class = serializers.MilestoneSerializers

    def get(self, request, contest_id, milestone_id):
        contest = get_object_or_404(contest_models.Contest, pk=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response({'detail': 'milestone is unrelated to contest'},
                    status=status.HTTP_400_BAD_REQUEST)
        data = self.get_serializer(milestone).data
        return Response(data)


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
