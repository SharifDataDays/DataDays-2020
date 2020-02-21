from django.shortcuts import render
from rest_framework.generics import GenericAPIView
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response
from apps.staff.serializers import *

# Create your views here.
class TeamView(GenericAPIView):
    serializer_class = TeamSerializer

    def get(self, request):
        data = TeamSerializer(self.get_queryset().get()).data
        return Response(data)

class StaffView(GenericAPIView):
    serializer_class = StaffSerializer

    def get(self, request):
        data = StaffSerializer(self.get_queryset().get()).data
        return Response(data)
