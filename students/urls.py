from django.urls import path
from .views import StudentListCreateView, StudentDetailView

urlpatterns = [
    path('', StudentListCreateView.as_view()),
    path('<int:pk>/', StudentDetailView.as_view()),
]
