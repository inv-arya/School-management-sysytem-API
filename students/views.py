import csv
import io
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from .models import Student
from accounts.models import User
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

class StudentCSVImportView(APIView):
    permission_classes = [IsAdminUser]

    def post(self, request, *args, **kwargs):
        file = request.FILES.get('file')
        if not file:
            return Response({'error': 'CSV file required'}, status=status.HTTP_400_BAD_REQUEST)

        decoded_file = file.read().decode('utf-8')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created_students = 0
        errors = []

        for i, row in enumerate(reader, start=2):  # start=2 to account for header
            try:
                student_data = {
                    'user': {
                        'username': row['username'],
                        'email': row['email'],
                        'password': row['password'] ,
                        'role': 'student'  # You can later send a reset link
                    },
                    'first_name': row['first_name'],
                    'last_name': row['last_name'],
                    'email': row['email'],
                    'phone_number': row['phone_number'],
                    'roll_number': row['roll_number'],
                    'grade': row['grade'],
                    'date_of_birth': row['date_of_birth'],
                    'admission_date': row['admission_date'],
                    'status': row['status'],
                    'assigned_teacher': None  # or map by name/id if added to CSV
                }

                serializer = StudentSerializer(data=student_data)
                if serializer.is_valid():
                    serializer.save()
                    created_students += 1
                else:
                    errors.append({'line': i, 'error': serializer.errors})

            except Exception as e:
                errors.append({'line': i, 'error': str(e)})

        return Response({
            'message': f'{created_students} students imported successfully',
            'errors': errors
        }, status=status.HTTP_200_OK)