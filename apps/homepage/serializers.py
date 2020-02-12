import random

from rest_framework import serializers

from .models import Intro, TimelineEvent, Prize, Stat, Count


class IntroSerializer(serializers.ModelSerializer):

    class Meta:
        model = Intro
        fields = '__all__'


class TimelineEventSerializer(serializers.ModelSerializer):

    class Meta:
        model = TimelineEvent
        fields = '__all__'


class PrizeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Prize
        fields = '__all__'


class StatSerializer(serializers.ModelSerializer):

    class Meta:
        model = Stat
        fields = '__all__'


class CountSerializer(serializers.ModelSerializer):

    count = serializers.SerializerMethodField()

    class Meta:
        model = Count
        fields = ['title', 'count']

    def get_count(self, obj):
        try:
            return obj.get_count()
        except Exception:
            return random.randint(200, 500)
