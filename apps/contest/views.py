from django.shortcuts import get_object_or_404
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.contest.services.create_team_tasks import GetOrCreateTeamTasks
from apps.contest.services.trial_services.trial_corrector import TrialCorrector
from apps.contest.services.trial_services.trial_submit_validation import TrialSubmitValidation

from apps.participation.models import Team, Participant

from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class ContestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = serializers.ContestSerializer

    def get(self, request, contest_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        if request.user.participant is None:
            new_team = Team(contest=contest, name=request.user.username)
            new_team.save()
            new_participant = Participant(user=request.user, team=new_team)
            new_participant.save()
        data = self.get_serializer(contest).data
        return Response(data={'contest': data})


class MilestoneAPIView(GenericAPIView):
    queryset = contest_models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer

    def get(self, request, contest_id, milestone_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_400_BAD_REQUEST)
        team = request.user.participant.team
        team_task_creator = GetOrCreateTeamTasks(team=team, milestone=milestone)
        team_tasks = team_task_creator.get_team_tasks()
        data = self.get_serializer(milestone).data
        return Response(data={'milestone': data}, status=status.HTTP_200_OK)


class CreateTrialAPIView(GenericAPIView):
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TrialSerializer

    def get(self, request, contest_id, milestone_id, task_id):
        maker = trial_maker.TrialMaker(request, contest_id, milestone_id, task_id)
        trial, errors = maker.make_trial()
        if trial is None:
            return Response(data={'errors': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = self.get_serializer(trial).data
        return Response(data={'trial': data}, status=status.HTTP_200_OK)


class SubmitTrialAPIView(GenericAPIView):

    def post(self, request, contest_id, milestone_id, task_id, trial_id):
        trial_submitter = TrialSubmitValidation(request, contest_id, milestone_id, task_id, trial_id)
        trial, valid, errors = trial_submitter.validate()
        if not valid:
            return Response(data={'errors', errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        trial_corrector = TrialCorrector(trial=trial)
        score = trial_corrector()
        return Response(data={'trial': trial, 'score': score}, status=status.HTTP_200_OK)
