from django.urls import path

from apps.participation import views

urlpatterns = [
    path('teams/', views.TeamListAPIView.as_view()),
    path('<int:contest_id>/team/', views.TeamAPIView.as_view()),
    path('<int:contest_id>/invitation/', views.InvitationAPIView.as_view()),
]
