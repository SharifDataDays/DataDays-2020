from rest_framework.generics import GenericAPIView
from rest_framework.response import Response

from apps.rrank.models import TeamNum
from apps.rrank.serializers import TeamNumSerializer


class TeamNumView(GenericAPIView):
    queryset = TeamNum.objects.all()
    serializer_class = TeamNumSerializer

    def get_serializer_context(self):
        return {'token': self.kwargs['token']}

    def get(self, request, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            return Response(data=serializer.data, status=200)

    def post(self, request, token):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
        return Response(data=serializer.data, status=200)
