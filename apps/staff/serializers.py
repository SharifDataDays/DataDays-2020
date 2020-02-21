from rest_framework import serializers
from apps.staff.models import *


class StaffSerializer(serializers.ModelSerializer):

    class Meta:
        model = Staff
        fields = ['image', 'title_en', 'title_fa', 'name_en', 'name_fa']


class TeamSerializer(serializers.ModelSerializer):
    staffs = StaffSerializer(many=True)


    class Meta:
        model = Team
        fields = ['staffs', 'title_en', 'title_fa']

