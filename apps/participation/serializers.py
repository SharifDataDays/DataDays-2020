from django.contrib.auth.models import User

from rest_framework import serializers

from apps.participation.models import Team, Participant, Invitation, Badge
from apps.contest.models import Contest


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class ParticipantSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Participant
        fields = ['id', 'user']


class InvitationSerializer(serializers.ModelSerializer):
    contest_id = serializers.CharField(source='contest.id')
    team = serializers.CharField(source='team.name', read_only=True)
    participant = serializers.CharField(source='participant.user.username')
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'contest_id', 'team', 'participant', 'accept']

    def validate(self, data):
        filtered_contests = Contest.objects.filter(id=data['contest']['id'])
        if filtered_contests.count() != 1:
            raise serializers.ValidationError('requested contest not found')
        contest = filtered_contests.get()

        filtered_users = User.objects.filter(username=data['participant'])
        if filtered_users.count() != 1:
            raise serializers.ValidationError('requested user not found')
        participant = filtered_users.get().participant
        team = self.context.get('view').request.user.participant.teams.get(contest=contest)
        if team.finalized():
            raise serializers.ValidationError(f'your team is finalized')
        participant_team = participant.teams.filter(contest=contest)
        if participant_team.count() != 1:
            raise serializers.ValidationError(f'requested user\'s is finalized')
        participant_team = participant_team.get()

        current_team_size = team.participants.all().count()
        num_invites = team.invitations.count()
        team_size = team.contest.team_size
        if not current_team_size + num_invites < team_size:
            raise serializers.ValidationError(
                    'number of team members and open invitations exeeds team size'
                )
        return data

    def create(self, validated_data):
        contest = Contest.objects.get(id=validated_data['contest']['id'])
        team = self.context.get('view').request.user.participant.teams.get(contest=contest)
        participant_user = User.objects.get(username=validated_data['participant']['user']['username'])
        if not hasattr(participant_user, 'participant'):
            Participant.objects.create(user=participant_user)
        participant = participant_user.participant

        if Invitation.objects.filter(
                contest=contest,
                team=team,
                participant=participant).count() != 0:
            raise serializers.ValidationError('same invitation already exists')
        return Invitation.objects.create(
                contest=contest,
                team=team,
                participant=participant)


class InvitationActionSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Invitation()._meta.get_field('id'), write_only=True)

    # Both team and participant may use this field.
    # team can only use False value to cancel invite.
    # participant can use True and False to accept and reject.
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'accept']

    def validate(self, data):
        filtered_invitations = Invitation.objects.filter(id=data['id'])
        if filtered_invitations.count() != 1:
            raise serializers.ValidationError('requested invitation not found')
        invitation = filtered_invitations.get()
        if self.context.get('view').request.user.participant not in \
                invitation.team.participants.all() + [invitation.participant]:
            raise serializers.ValidationError('requested invitation is not yours')
        return data

    def update(self, instance, validated_data):
        if self.context.get('view').request.user.participant in instance.team.participants:
            if validated_data['accept']:
               raise serializers.ValidationError(
                       'cant send True for \'accept\' as invitation sender'
                    )
        elif self.context.get('view').request.user.participant == instance.participant:
            if validated_data['accept']:
                instance.participant.teams.filter(contest=instance.contest).delete()
                instance.participant.teams.add(instance.team)
        else:
            raise serializers.ValidationError('invite not for user')
        instance.delete()
        return instance


class InvitationListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    invitations = InvitationSerializer(source='invitations', many=True, read_only=True)
    team_invitations = InvitationSerializer(source='team.invitations', many=True, read_only=True)

    class Meta:
        model = Participant
        fields = ['name', 'invitations', 'team_invitations']


class TeamSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    invitations = InvitationSerializer(source='invitations', many=True, read_only=True)
    name_finalized = serializers.BooleanField(read_only=True)
    finalize = serializers.BooleanField(write_only=True)

    class Meta:
        model = Team
        fields = ['id', 'contest', 'name', 'name_finalized', 'finalize', 'participants', 'invitations']

    def update(self, instance, validated_data):
        if instance.name_finalized:
            raise serializers.ValidationError('Team info finalized')
        if validated_data.pop('finalize'):
            instance.name_finalized = True
        instance.name = validated_data['name']
        instance.save()
        return instance


class BadgeSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Badge
        fields = ['id', 'image', 'milestone', 'teams']

