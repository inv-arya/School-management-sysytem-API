from django.urls import path
from .views import AssignmentCreateView,AssignmentListView,AssignmentDetailView,AssignmentSubjectsView,SubmissionUpdateView,TeacherAssignmentSubmissionsView,SubmissionDetailView,OverdueSubmissionListView,OverdueSubmissionExportView

urlpatterns = [
    path('', AssignmentCreateView.as_view(), name='assignment-create'),
    path('list/', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
    path('subjects/', AssignmentSubjectsView.as_view(), name="student-assignment-subjects"),
    path('submissions/', SubmissionUpdateView.as_view(), name='submission-update'),
    path('<int:pk>/submissions/', TeacherAssignmentSubmissionsView.as_view(), name='teacher-assignment-submissions'),
    path('submissions/<int:assignment_id>/', SubmissionDetailView.as_view(), name='submission-detail'),
    path('submissions/overdue/<int:assignment_id>/', OverdueSubmissionListView.as_view(), name='overdue-submissions'),
    path('submissions/overdue/<int:assignment_id>/export/', OverdueSubmissionExportView.as_view(), name='overdue-submissions-export'),
]
