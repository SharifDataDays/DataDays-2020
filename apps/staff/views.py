from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from apps.staff.serializers import *
from django.http import Http404


# Create your views here.
class TeamView(GenericAPIView):
    serializer_class = TeamSerializer
    queryset = Team.objects.all().order_by('order')

    def get(self, request):
        try:
            data = TeamSerializer(self.get_queryset(), many=True).data
            return Response(data)
        except Team.DoesNotExist:
            raise Http404

class StaffView(GenericAPIView):
    serializer_class = StaffSerializer
    queryset = Staff.objects.all()

    def get(self, request):
        try:
            data = StaffSerializer(self.get_queryset(), many=True).data
            return Response(data)
        except Staff.DoesNotExist:
            raise Http404
