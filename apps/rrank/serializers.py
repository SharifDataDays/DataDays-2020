from rest_framework import serializers
from rest_framework.validators import UniqueValidator

from apps.rrank.models import TeamNum, TeamToken


class TeamNumSerializer(serializers.ModelSerializer):

    number = serializers.IntegerField()
    team = serializers.CharField(read_only=True,
                                 validators=[UniqueValidator(
                                         queryset=TeamNum.objects.all())]
                                 )

    class Meta:
        model = TeamNum
        fields = ['number', 'team']

    def validate(self, data):
        if 'token' not in self.context:
            raise serializers.ValidationError(
                'Token missing in serializer context')
        try:
            tt = TeamToken.objects.get(token=self.context['token'])
        except Exception as e:
            raise serializers.ValidationError(
                f'Execption in tt: {str(e)}')
        data['team'] = tt.team
        return data

    def create(self, validated_data):
        team = validated_data['team']
        number = validated_data['number']
        tt = TeamNum.objects.filter(team=team)
        if tt.count() == 0:
            return TeamNum.objects.create(team=team, number=number)
        elif tt.count() == 1:
            return self.update(tt.get(), validated_data)
        else:
            raise serializers.ValidationError('TeamNum exists')

    def update(self, instance, validated_data):
        instance.number = validated_data['number']
        instance.save()
        return instance
