from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework import status

from apps.contest.services.trial_services.trial_corrector import TrialCorrector
from apps.contest.services.trial_services.trial_submit_validation import TrialSubmitValidation
from . import models as contest_models, serializers
from apps.contest.services.trial_services import trial_maker


class CreateTrialAPIView(GenericAPIView):
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TrialSerializer

    def get(self, request):
        maker = trial_maker.TrialMaker(request)
        trial, errors = maker.make_trial()
        if trial is None:
            return Response(data={'errors': errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        data = self.get_serializer(trial).data
        return Response(data={'trial': data}, status=status.HTTP_200_OK)


class SubmitTrialAPIView(GenericAPIView):

    def post(self, request):
        trial_submitter = TrialSubmitValidation(request=request)
        trial, valid, errors = trial_submitter.validate()
        if not valid:
            return Response(data={'errors', errors}, status=status.HTTP_406_NOT_ACCEPTABLE)
        trial_corrector = TrialCorrector(trial=trial)
        score = trial_corrector()
        return Response(data={'trial': trial, 'score': score}, status=status.HTTP_200_OK)


class UserTasksListAPIView(GenericAPIView):
    queryset = contest_models.Task.objects.all()
    serializer_class = serializers.TaskSerializer

    def get(self, request, username):
        tasks = self.get_queryset().filter(user__username=username)
        data = self.get_serializer(tasks, many=True).data
        return Response(data={'user': username, 'tasks': data}, status=status.HTTP_200_OK)
