import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,IsAdminUser
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

class StudentCSVExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="students.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email', 'Phone Number', 'Roll Number',
            'Grade', 'Date of Birth', 'Admission Date', 'Status', 'Assigned Teacher'
        ])

        for student in Student.objects.select_related('assigned_teacher', 'user'):
            writer.writerow([
                student.first_name,
                student.last_name,
                student.email,
                student.phone_number,
                student.roll_number,
                student.grade,
                student.date_of_birth,
                student.admission_date,
                student.status,
                student.assigned_teacher.user.username if student.assigned_teacher and student.assigned_teacher.user else ''
            ])

        return response
