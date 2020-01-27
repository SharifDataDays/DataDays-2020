from django.urls import path

from . import views

app_name = 'contest'

urlpatterns = [
    path('', views.ContestAPIView.as_view()),
    path('<int:contest_id>/', views.ContestAPIView.as_view()),
    path('<int:contest_id>/milestone/<int:milestone_id>/', views.MilestoneAPIView.as_view()),
    path('<int:contest_id>/milestone/<int:milestone_id>/task/<int:task_id>/', views.TaskAPIView.as_view()),
    path('<int:contest_id>/milestone/<int:milestone_id>/task/<int:task_id>/trial/<int:trial_id>/', views.TrialAPIView.as_view()),
]
