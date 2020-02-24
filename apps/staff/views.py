from django.http import Http404

from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.staff.models import Team, SubTeam, Staff
from apps.staff.serializers import (
    TeamSerializer, StaffSerializer, SubTeamSerializer
)


class TeamView(GenericAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all().order_by('id').order_by('order')

    def get(self, request):
        try:
            data = TeamSerializer(self.get_queryset(), many=True).data
            return Response(data)
        except Team.DoesNotExist:
            raise Http404


class StaffView(GenericAPIView):
    serializer_class = StaffSerializer
    queryset = Staff.objects.all().order_by('order')

    def get(self, request):
        try:
            data = StaffSerializer(self.get_queryset(), many=True).data
            return Response(data)
        except Staff.DoesNotExist:
            raise Http404


class SubteamView(GenericAPIView):
    serializer_class = SubTeamSerializer
    queryset = SubTeam.objects.all()

    def get(self, request):
        try:
            data = SubTeamSerializer(self.get_queryset(), many=True).data
            return Response(data)
        except Staff.DoesNotExist:
            raise Http404
