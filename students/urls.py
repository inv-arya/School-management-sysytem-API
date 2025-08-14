from django.urls import path
from .views import StudentListCreateView, StudentDetailView,StudentCSVExportView,StudentCSVImportView,StudentsByTeacherView

urlpatterns = [
    path('', StudentListCreateView.as_view()),
    path('by-teacher/<int:teacher_id>/', StudentsByTeacherView.as_view(), name='students-by-teacher'),
    path('<int:pk>/', StudentDetailView.as_view()),
    path('export/csv/', StudentCSVExportView.as_view(), name='student-export-csv'),
    path('import-csv/', StudentCSVImportView.as_view(), name='student-import-csv'),
]
