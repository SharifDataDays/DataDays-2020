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


class TeamSerializer(serializers.ModelSerializer):
    participants = ParticipantSerializer(many=True, read_only=True)
    name_finalized = serializers.BooleanField(read_only=True)
    finalize = serializers.BooleanField(write_only=True)

    class Meta:
        model = Team
        fields = ['id', 'contest', 'name', 'name_finalized', 'finalize', 'participants']

    def update(self, instance, validated_data):
        if instance.name_finalized:
            raise serializers.ValidationError('Team info finalized')
        if validated_data.pop('finalize'):
            instance.name_finalized = True
        instance.name = validated_data['name']
        instance.save()
        return instance


class InvitationSerializer(serializers.ModelSerializer):
    contest_id = serializers.CharField(source='contest.id')
    sender = serializers.CharField(source='sender.user.username', read_only=True)
    reciever = serializers.CharField(source='reciever.user.username')
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'contest_id', 'sender', 'reciever', 'accept']

    def check_finalized_teams(self, username, contest):
        filtered_users = User.objects.filter(username=username)
        if filtered_users.count() != 1:
            raise serializers.ValidationError('requested user not found')
        user = filtered_users.get()
        team = None
        if hasattr(user, 'participant'):
            if hasattr(user.participant, 'teams'):
                filtered_teams = user.participant.teams.filter(contest=contest)
                if filtered_teams.count() == 1:
                    team = filtered_teams.get()
                    if team.finalized():
                        raise serializers.ValidationError(f'{username}\'s team is finalized')
        return user, team

    def validate(self, data):
        filtered_contests = Contest.objects.filter(id=data['contest']['id'])
        if filtered_contests.count() != 1:
            raise serializers.ValidationError('requested contest not found')
        contest = filtered_contests.get()
        if data['sender'] == data['reciever']:
            raise serializers.ValidationError(
                    'sender and reciever can\'t be same'
                )
        sender, sender_team = self.check_finalized_teams(self.context.get('view').request.user.username, contest)
        self.check_finalized_teams(data['reciever']['user']['username'], contest)

        current_team_size = sender_team.participants.all().count()
        num_invites = Invitation.objects.filter(sender__user=sender, contest=sender_team.contest).count()
        team_size = sender_team.contest.team_size
        if not current_team_size + num_invites < team_size:
            raise serializers.ValidationError(
                    'number of team members and open invitations exeeds team size'
                )
        return data

    def create(self, validated_data):
        contest = Contest.objects.get(id=validated_data['contest']['id'])
        sender = self.context.get('view').request.user
        reciever = User.objects.get(username=validated_data['reciever']['user']['username'])
        if not hasattr(reciever, 'participant'):
            Participant.objects.create(user=reciever)

        if Invitation.objects.filter(
                contest=contest,
                sender=sender.participant,
                reciever=reciever.participant).count() != 0:
            raise serializers.ValidationError('same invitation already exists')
        return Invitation.objects.create(
                contest=contest,
                sender=sender.participant,
                reciever=reciever.participant)


class InvitationActionSerializer(serializers.ModelSerializer):
    id = serializers.ModelField(model_field=Invitation()._meta.get_field('id'), write_only=True)

    # Both sender and reciever may use this field.
    # sender can only use False value to cancel invite.
    # reciever can use True and False to accept and reject.
    accept = serializers.BooleanField(write_only=True)

    class Meta:
        model = Invitation
        fields = ['id', 'accept']

    def validate(self, data):
        filtered_invitations = Invitation.objects.filter(id=data['id'])
        if filtered_invitations.count() != 1:
            raise serializers.ValidationError('requested invitation not found')
        invitation = filtered_invitations.get()
        if self.context.get('view').request.user not in \
                [invitation.sender.user, invitation.reciever.user]:
            raise serializers.ValidationError('requested invitation is not yours')
        return data

    def update(self, instance, validated_data):
        if self.context.get('view').request.user == instance.sender.user:
            if validated_data['accept']:
               raise serializers.ValidationError(
                       'cant send True for \'accept\' as invitation sender'
                    )
        elif self.context.get('view').request.user == instance.reciever.user:
            if validated_data['accept']:
                instance.reciever.teams.filter(contest=instance.contest).delete()
                instance.reciever.teams.add(
                        instance.sender.teams.get(contest=instance.contest)
                    )
        else:
            raise serializers.ValidationError('invite not for user')
        instance.delete()
        return instance


class InvitationListSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    sent = InvitationSerializer(source='invitations_sent', many=True, read_only=True)
    recieved = InvitationSerializer(source='invitations_recieved', many=True, read_only=True)

    class Meta:
        model = Participant
        fields = ['username', 'sent', 'recieved']


class BadgeSerializer(serializers.ModelSerializer):
    teams = TeamSerializer(many=True, read_only=True)

    class Meta:
        model = Badge
        fields = ['id', 'image', 'milestone', 'teams']

