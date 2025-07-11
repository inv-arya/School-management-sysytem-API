from django.urls import path
from .views import TeacherListCreateView, TeacherDetailView, TeacherCSVExportView

urlpatterns = [
    path('', TeacherListCreateView.as_view(), name='teacher-list-create'),
    path('<int:pk>/', TeacherDetailView.as_view(), name='teacher-detail'),
    path('export/csv/', TeacherCSVExportView.as_view(), name='teacher-export-csv'),
]
