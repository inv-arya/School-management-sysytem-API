from django.urls import path
from .views import AssignmentCreateView,AssignmentListView,AssignmentDetailView,AssignmentSubjectsView,SubmissionUpdateView,TeacherAssignmentSubmissionsView

urlpatterns = [
    path('', AssignmentCreateView.as_view(), name='assignment-create'),
    path('list/', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('subjects/', AssignmentSubjectsView.as_view(), name="student-assignment-subjects"),
    path('submissions/', SubmissionUpdateView.as_view(), name='submission-update'),
    path('<int:pk>/submissions/', TeacherAssignmentSubmissionsView.as_view(), name='teacher-assignment-submissions'),
]