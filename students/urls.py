from django.urls import path
from .views import StudentListCreateView, StudentDetailView,StudentCSVExportView

urlpatterns = [
    path('', StudentListCreateView.as_view()),
    path('<int:pk>/', StudentDetailView.as_view()),
    path('export/csv/', StudentCSVExportView.as_view(), name='student-export-csv'),
]
