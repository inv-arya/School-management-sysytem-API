from django.urls import path
from .views import AssignmentCreateView,AssignmentListView,AssignmentDetailView,AssignmentSubjectsView

urlpatterns = [
    path('', AssignmentCreateView.as_view(), name='assignment-create'),
    path('list/', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path("subjects/", AssignmentSubjectsView.as_view(), name="student-assignment-subjects"),
]