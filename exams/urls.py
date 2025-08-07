from django.urls import path
from .views import ExamCreateView, AvailableExamListView, MyExamsView, AttemptExamView,ExamDetailDeleteView

urlpatterns = [
    path('create/', ExamCreateView.as_view(), name='exam-create'),
    path('available/', AvailableExamListView.as_view(), name='exam-list'),
    path('my/', MyExamsView.as_view(), name='my-exams'),
    path('attempt/', AttemptExamView.as_view(), name='exam-attempt'),
    path('<int:pk>/', ExamDetailDeleteView.as_view(), name='exam-detail-update-delete'),
]

