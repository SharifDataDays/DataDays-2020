from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser, FormParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.contest.permissions import UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks
from apps.contest.services.trial_services.trial_submit_validation import TrialSubmitValidation
from apps.contest.tasks import judge_trials

from apps.participation.models import Team, Participant

from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class ContestsListAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant]
    serializer_class = serializers.ContestAsAListItemSerializer
    queryset = contest_models.Contest.objects.all()

    def get(self, request):
        data = self.get_serializer(self.get_queryset(), many=True).data
        return Response(data={'contests': data}, status=status.HTTP_200_OK)


class ContestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest]
    serializer_class = serializers.ContestSerializer

    def get_object(self, contest_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        if contest.team_size > 1:
            self.check_object_permissions(self.request, contest)
        else:
            Team.get_team(self.request.user.participant, contest)
        return contest

    def get(self, request, contest_id):
        contest = self.get_object(contest_id)
        data = self.get_serializer(contest).data
        return Response(data={'contest': data})


class MilestoneAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest]
    queryset = contest_models.Milestone.objects.all()
    serializer_class = serializers.MilestoneSerializer

    def get(self, request, contest_id, milestone_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)

        data = self.get_serializer(milestone).data
        return Response(data={'milestone': data}, status=status.HTTP_200_OK)


class CreateTrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TrialSerializer

    def get(self, request, contest_id, milestone_id, task_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)

        maker = trial_maker.TrialMaker(request, contest_id, milestone_id, task_id)
        trial, errors = maker.make_trial()
        if trial is None:
            team_task = get_object_or_404(
                    contest_models.TeamTask,
                    task_id=task_id,
                    team=request.user.participant.teams.get(contest=contest)
                )
            trials = contest_models.Trial.filter(team_task=team_task)
            if trials.count() == 1:
                trial = trials.get()
        else:
            judge_trials.apply_async(trial.pk, countdown=int(60*60*trial.task.trial_time))
        if trial is None:
            return Response(data={'detail': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = self.get_serializer(trial).data
        return Response(data={'trial': data}, status=status.HTTP_200_OK)


class SubmitTrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    parser_classes = (MultiPartParser, JSONParser)
    serializer_class = serializers.TrialPostSerializer

    def post(self, request, contest_id, milestone_id, task_id, trial_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)
        trial = get_object_or_404(contest_models.Trial, id=trial_id)
        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)
        if trial not in team_task.trials.all():
            return Response(data={'detail': 'This trial is not yours. bitch'}, status=status.HTTP_406_NOT_ACCEPTABLE)

        trial_submitter = TrialSubmitValidation(request, contest_id, milestone_id, task_id, trial_id)
        trial, valid, errors = trial_submitter.validate()
        if not valid:
            return Response(data={'errors': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if trial.final_submit:
            trial.submit_time = timezone.now()
            trial.save()
            judge_trials.delay(trial.pk)
        else:
            trial.save()

        return Response(data={'trial': self.get_serializer(trial).data}, status=status.HTTP_200_OK)


class ContentFinishedAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]

    def get(self, request, contest_id, milestone_id, task_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)
        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)
        team_task.content_finished = True
        team_task.save()
        return Response(data={'detail': 'done'}, status=status.HTTP_200_OK)
