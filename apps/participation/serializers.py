from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer

from apps.contest.serializers import MilestoneSerializer

from . import models as participant_models


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ParticipantSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = participant_models.Participant
        fields = ['user']


class TeamSerializer(ModelSerializer):
    milestone = MilestoneSerializer()
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = participant_models.Team
        fields = ['milestone', 'participants']


class InvitationSerializer(ModelSerializer):
    host = UserSerializer()
    guest = UserSerializer()

    class Meta:
        model = participant_models.Invitation
        fields = ['host', 'guest']
