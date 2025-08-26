from django.urls import path
from .views import AssignmentCreateView,AssignmentListView,AssignmentDetailView

urlpatterns = [
    path('', AssignmentCreateView.as_view(), name='assignment-create'),
    path('list/', AssignmentListView.as_view(), name='assignment-list'),
    path('<int:pk>/', AssignmentDetailView.as_view(), name='assignment-detail'),
]