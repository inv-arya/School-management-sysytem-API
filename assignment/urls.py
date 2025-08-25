from django.urls import path
from .views import AssignmentCreateView

urlpatterns = [
    path('', AssignmentCreateView.as_view(), name='assignment-create'),
]