from django.urls import path

from apps.rrank.views import TeamNumView


urlpatterns = [
    path('<slug:token>/', TeamNumView.as_view()),
]
