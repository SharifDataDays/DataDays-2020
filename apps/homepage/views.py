from rest_framework.response import Response
from rest_framework.generics import GenericAPIView


from apps.homepage.models import Intro, TimelineEvent, Prize, Count
from apps.homepage.serializers import \
    IntroSerializer, TimelineEventSerializer, PrizeSerializer, CountSerializer


class HomepageView(GenericAPIView):

    def get(self, request):
        data = {
                'intro': IntroSerializer(Intro.objects.last()).data,
                'timeline': TimelineEventSerializer(
                    TimelineEvent.objects.all().order_by('id')
                    .order_by('order'), many=True).data,
                'prizes': PrizeSerializer(
                    Prize.objects.all().order_by('id'), many=True).data,
                'counts': list(CountSerializer(
                    Count.objects.filter(show=True)
                    .order_by('id'), many=True).data)[0:3],
        }
        return Response(data)


class TermsOfUseView(GenericAPIView):

    def get(self, request):
        data = {
                'term': Intro.objects.first().term_of_use
                }
        return Response(data)
