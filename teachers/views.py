

from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Teacher
from .serializers import TeacherSerializer
from accounts.permissions import TeacherAccessPermission
from rest_framework.permissions import IsAuthenticated

class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminUser]  # Only admins can create/list teachers

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, TeacherAccessPermission]
