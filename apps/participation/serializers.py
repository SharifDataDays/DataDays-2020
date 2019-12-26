from django.contrib.auth.models import User

from rest_framework.serializers import ModelSerializer

from . import models as participant_models


class UserSerializer(ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ParticipantSerializer(ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = participant_models.Participant
        fields = ['id', 'user']


class TeamSerializer(ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = participant_models.Team
        fields = ['id', 'milestone', 'participants']


class InvitationSerializer(ModelSerializer):
    host = UserSerializer()
    guest = UserSerializer()

    class Meta:
        model = participant_models.Invitation
        fields = ['id', 'host', 'guest']


class BadgeSerializer(ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = participant_models.Badge
        fields = ['id', 'image', 'milestone', 'teams']
