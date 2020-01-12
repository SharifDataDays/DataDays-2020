from django.urls import path

from .views import QuestionsListAPIView, QuestionTestAPIView

app_name = 'question'

urlpatterns = [
    path('test/', QuestionTestAPIView.as_view()),
]
