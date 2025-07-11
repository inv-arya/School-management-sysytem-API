from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Student
from .serializers import StudentSerializer
from accounts.permissions import StudentAccessPermission
from rest_framework.exceptions import PermissionDenied


class StudentListCreateView(generics.ListCreateAPIView):
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'admin':
            return Student.objects.all()
        elif user.role == 'teacher':
            return Student.objects.filter(assigned_teacher__user=user)
        elif user.role == 'student':
            return Student.objects.filter(user=user)
        return Student.objects.none()
    def post(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            raise PermissionDenied("Only admins can create students.")
        return super().post(request, *args, **kwargs)

class StudentDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Student.objects.all()
    serializer_class = StudentSerializer
    permission_classes = [IsAuthenticated, StudentAccessPermission]
