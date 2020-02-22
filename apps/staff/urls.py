from django.urls import path

from apps.staff.views import TeamView

urlpatterns = [

    path('', TeamView.as_view()),
]
