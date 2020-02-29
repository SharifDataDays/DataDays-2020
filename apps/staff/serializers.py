from rest_framework import serializers
from apps.staff.models import Staff, SubTeam, Team


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ['image', 'title_en', 'title_fa',
                  'name_en', 'name_fa', 'order',
                  'link', 'description']


class SubTeamSerializer(serializers.ModelSerializer):
    staffs = serializers.SerializerMethodField()

    class Meta:
        model = SubTeam
        fields = ['staffs', 'title_en', 'title_fa', 'order']

    def get_staffs(self, obj):
        return [
            StaffSerializer(staff).data
            for staff in obj.staffs.all().order_by('order')
        ]


class TeamSerializer(serializers.ModelSerializer):
    subteams = SubTeamSerializer(many=True)

    class Meta:
        model = Team
        fields = ['subteams', 'title_en', 'title_fa', 'order']
