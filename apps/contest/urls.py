from django.urls import path

from . import views

app_name = 'contest'

urlpatterns = [

    path('<contest_title>/', views.ContestAPIView.as_view, name='contest'),
    path('<contest_title>/<int:milestone_id>/', views.MilestoneAPIView.as_view, name='milestone'),
    path('<contest_title>/<int:milestone_id>/<int:task_id>/', views.CreateTrialAPIView.as_view, name='create_trial'),
    path('<contest_title>/<int:milestone_id>/<ind:task_id>/<int:trial_id>/', views.SubmitTrialAPIView.as_view,
         name='submit_trial')

]
