from django.urls import path

from apps.staff.views import *

urlpatterns = [

    path('', TeamView.as_view()),
]
