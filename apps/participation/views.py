from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

from rest_framework import status, permissions
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.participation.models import Team, Participant, Invitation
from apps.participation.serializers import TeamListSerializer, TeamSerializer, ParticipantSerializer, \
        InvitationListSerializer, InvitationSerializer, InvitationActionSerializer
from apps.participation.permissions import UserHasParticipant, UserHasTeamInContest

from apps.contest.models import Contest


class TeamListAPIView(GenericAPIView):
    queryset = User.objects.all()
    serializer_class = TeamListSerializer
    permission_classes = [permissions.IsAuthenticated, UserHasParticipant]

    def get(self, request):
        data = self.get_serializer(request.user).data
        return Response(data)


class TeamAPIView(GenericAPIView):
    queryset = Team.objects.all()
    serializer_class = TeamSerializer
    permission_classes = [
        permissions.IsAuthenticated, UserHasParticipant,
        UserHasTeamInContest
    ]

    def get(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        if contest.team_size == 1:
            return Response(data={'detail': 'requested contest is individual'}, status=406)
        self.check_object_permissions(self.request, contest)
        team = request.user.participant.teams.get(contest=contest)
        data = self.get_serializer(team).data
        return Response(data)

    def put(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        self.check_object_permissions(self.request, contest)
        team = request.user.participant.teams.get(contest=contest)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.instance = team
            serializer.save()
        return Response(serializer.data)


class InvitationAPIView(GenericAPIView):
    queryset = Invitation.objects.all()
    permission_classes = [
        permissions.IsAuthenticated, UserHasParticipant, UserHasTeamInContest
    ]

    def get_serializer_class(self):
        serializer_map = {
            'GET': InvitationListSerializer,
            'POST': InvitationSerializer,
            'PUT': InvitationActionSerializer,
        }
        return serializer_map[self.request.method]

    def get(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        self.check_object_permissions(self.request, contest)
        self.contest = contest
        data = self.get_serializer(request.user.participant.teams.get(contest=contest)).data
        return Response(data)

    def post(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        self.check_object_permissions(self.request, contest)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(data={'detail': 'invitation sent'})

    def put(self, request, contest_id):
        contest = get_object_or_404(Contest, id=contest_id)
        self.check_object_permissions(self.request, contest)
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            invitation = get_object_or_404(self.get_queryset(), id=serializer.validated_data['id'])
            serializer.instance = invitation
            serializer.save()
        return Response(data={'detail': 'done'})

