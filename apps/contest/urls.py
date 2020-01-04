from django.urls import path

from . import views

app_name = 'contest'

urlpatterns = [

    path('<int:contest_id>/', views.ContestAPIView.as_view(), name='contest'),
    path('<int:contest_id>/<int:milestone_id>/', views.MilestoneAPIView.as_view(), name='milestone'),
    path('<int:contest_id>/<int:milestone_id>/<int:task_id>/', views.CreateTrialAPIView.as_view(), name='create_trial'),
    path('<int:contest_id>/<int:milestone_id>/<int:task_id>/content_finished/', views.ContentFinishedAPIView.as_view(), name='content_finished'),
    path('<int:contest_id>/<int:milestone_id>/<int:task_id>/<int:trial_id>', views.SubmitTrialAPIView.as_view(),
         name='submit_trial'),

]

