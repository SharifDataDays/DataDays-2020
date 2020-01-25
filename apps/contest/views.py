import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.http.multipartparser import MultiPartParser as DjangoMultiPartParser

from rest_framework.generics import GenericAPIView
from rest_framework.parsers import FileUploadParser, MultiPartParser, JSONParser, FormParser, BaseParser
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import DataAndFiles
from rest_framework.exceptions import ParseError

from apps.contest.permissions import UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks
from apps.contest.services.trial_services.trial_submit_validation import TrialSubmitValidation
from apps.contest.tasks import judge_trials
from apps.contest.serializers import TrialSerializer

from apps.participation.models import Team, Participant

from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class ContestsListAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant]
    serializer_class = serializers.ContestAsAListItemSerializer
    queryset = contest_models.Contest.objects.filter(start_time__lt=timezone.now()).order_by('order')

    def get(self, request):
        data = self.get_serializer(self.get_queryset(), many=True).data
        return Response(data={'contests': data}, status=status.HTTP_200_OK)


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

    def get(self, request, contest_id):
        contest = self.get_object(contest_id)
        data = self.get_serializer(contest).data
        return Response(data={'contest': data})


class MilestoneAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Milestone.objects.filter(start_time__lt=timezone.now()).order_by('order')
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


class TrialListAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Task.objects.filter(milestone__start_time__lt=timezone.now()).order_by('order')
    serializer_class = serializers.TrialSerializer

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

        trials = team_task.trials.all()

        data = self.get_serializer(trials, many=True).data
        return Response(data={'trials': data}, status=status.HTTP_200_OK)


class CreateTrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    queryset = contest_models.Task.objects.filter(milestone__start_time__lt=timezone.now()).order_by('order')
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
            return Response(data={'detail': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        else:
            data = self.get_serializer(trial).data
        return Response(data={'trial': data}, status=status.HTTP_200_OK)


class MyMultiPartParser(BaseParser):

    media_type = 'multipart/form-data'

    def parse(self, stream, media_type=None, parser_context=None):
        """
        Parses the incoming bytestream as a multipart encoded form,
        and returns a DataAndFiles object.

        `.data` will be a `QueryDict` containing all the form parameters.
        `.files` will be a `QueryDict` containing all the form files.
        """

        try:
            parser_context = parser_context or {}
            request = parser_context['request']
            encoding = parser_context['encoding'] or settings.DEFAULT_CHARSET
            meta = request.META.copy()
            meta['CONTENT_TYPE'] = media_type
            upload_handlers = request.upload_handlers
            stream = request._request.__dict__['_stream'].__dict__['stream']
            parser = DjangoMultiPartParser(meta, stream, upload_handlers, encoding)
            data, files = parser.parse()
            if 'json' not in data:
                raise ParseError('Multipart form parse error: json missing!')
            try:
                data = json.loads(data['json'])
            except ValueError:
                raise ParseError('Malformed Json')
            return DataAndFiles(data, files)
        except Exception as e:
            raise ParseError(f'Multipart form parse error: {str(e)}')


class SubmitTrialAPIView(GenericAPIView):
    permission_classes = [IsAuthenticated, UserHasParticipant, UserHasTeamInContest, UserHasTeamTasks]
    parser_classes = (MyMultiPartParser,)
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
        if trial.submit_time is not None:
            return Response(data={'detail': 'This trial has already been submitted.'}, status=403)
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

        return Response(data={'trial': TrialSerializer(trial).data}, status=status.HTTP_200_OK)


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
