from django.urls import path

from .views import QuestionsListAPIView, QuestionTestAPIView

app_name = 'question'

urlpatterns = [
    path('questions/<question_type>', QuestionsListAPIView.as_view(), name='question_list'),
    path('test/', QuestionTestAPIView.as_view()),
]
