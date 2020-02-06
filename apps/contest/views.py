from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils import timezone

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from apps.contest.permissions import UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks
from apps.contest.services.trial_services.trial_submit_validation import TrialSubmitValidation
from apps.contest.tasks import judge_trials
from apps.contest.serializers import TrialSerializer
from apps.contest.parsers import MyMultiPartParser

from apps.participation.models import Team, Participant

from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class ContestAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest]
    serializer_class = serializers.ContestSerializer
    queryset = contest_models.Contest.objects.filter(start_time__lt=timezone.now()).order_by('order')

    def get_object(self, contest_id):
        contest = get_object_or_404(self.get_queryset(), id=contest_id)
        if contest.team_size > 1:
            self.check_object_permissions(self.request, contest)
        else:
            Team.get_team(self.request.user.participant, contest)
        return contest

    def get(self, request, contest_id=None):
        if contest_id is None:
            data = self.get_serializer(self.get_queryset(), many=True).data
            return Response(data={'contests': data}, status=status.HTTP_200_OK)

        contest = self.get_object(contest_id)
        data = self.get_serializer(contest).data
        return Response(data={'contest': data})


class MilestoneAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Milestone.objects.filter(start_time__lt=timezone.now()).order_by('order')
    serializer_class = serializers.MilestoneSerializer

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if 'context' in kwargs:
            kwargs['context'].update(self.get_serializer_context())
        else:
            kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get(self, request, contest_id, milestone_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)

        team = request.user.participant.teams.get(contest=contest)

        data = self.get_serializer(milestone, context={'team': team}).data
        return Response(data={'milestone': data}, status=status.HTTP_200_OK)


class TaskAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Task.objects.filter(milestone__start_time__lt=timezone.now()).order_by('order')
    serializer_class = serializers.TaskSerializer

    def get_serializer_context(self):
        print('boooooo'*100)
        print(self.__dict__)
        return super().get_serializer_context()

    def get_serializer(self, *args, **kwargs):
        serializer_class = self.get_serializer_class()
        if 'context' in kwargs:
            kwargs['context'].update(self.get_serializer_context())
        else:
            kwargs['context'] = self.get_serializer_context()
        return serializer_class(*args, **kwargs)

    def get(self, request, contest_id, milestone_id, task_id):
        contest = get_object_or_404(contest_models.Contest, id=contest_id)
        milestone = get_object_or_404(contest_models.Milestone, pk=milestone_id)
        task = get_object_or_404(contest_models.Task, id=task_id)
        if milestone.contest != contest:
            return Response(data={'detail': 'milestone is unrelated to contest'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        if task.milestone != milestone:
            return Response(data={'detail': 'task is unrelated to milestone'},
                            status=status.HTTP_406_NOT_ACCEPTABLE)
        self.check_object_permissions(self.request, contest)
        self.check_object_permissions(self.request, milestone)

        team = request.user.participant.teams.get(contest=contest)
        team_task = team.tasks.get(task_id=task_id)

        trials = list(team_task.trials.all())

        data = self.get_serializer(team_task.task, context={'trials': trials}).data
        return Response(data=data, status=status.HTTP_200_OK)

    def post(self, request, contest_id, milestone_id, task_id):
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
            return Response(data={'detail': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        return Response(data={'detail': 'ok'}, status=status.HTTP_200_OK)

    def put(self, request, contest_id, milestone_id, task_id):
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


class TrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    parser_classes = (MyMultiPartParser,)
    serializer_class = serializers.TrialPostSerializer

    def get(self, request, contest_id, milestone_id, task_id, trial_id):
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

        data = serializers.TrialSerializer(trial).data
        return Response(data=data, status=200)

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
        if trial.submit_time is not None:
            return Response(data={'detail': 'This trial has already been submitted.'}, status=406)
        trial_submitter = TrialSubmitValidation(request, contest_id, milestone_id, task_id, trial_id)
        trial, valid, errors = trial_submitter.validate()
        if not valid:
            return Response(data={'errors': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)

        if trial_submitter.final_submit:
            trial.submit_time = timezone.now()
            trial.save()
            judge_trials.delay(trial.pk)
        else:
            trial.save()

        return Response(data={'detail': 'Trial submitted!'}, status=status.HTTP_200_OK)

