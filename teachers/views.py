import csv
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import generics
from rest_framework.permissions import IsAdminUser
from .models import Teacher
from .serializers import TeacherSerializer
from accounts.permissions import TeacherAccessPermission
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


class TeacherListCreateView(generics.ListCreateAPIView):
    queryset = Teacher.objects.filter(status='active')
    serializer_class = TeacherSerializer
    permission_classes = [IsAdminUser]  

class TeacherDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Teacher.objects.all()
    serializer_class = TeacherSerializer
    permission_classes = [IsAuthenticated, TeacherAccessPermission]

class TeacherCSVExportView(APIView):
    permission_classes = [IsAdminUser]

    def get(self, request):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="teachers.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'First Name', 'Last Name', 'Email', 'Phone Number',
            'Subject Specialization', 'Employee ID', 'Date of Joining', 'Status'
        ])

        for teacher in Teacher.objects.select_related('user'):
            writer.writerow([
                teacher.first_name,
                teacher.last_name,
                teacher.email,
                teacher.phone_number,
                teacher.subject_specialization,
                teacher.employee_id,
                teacher.date_of_joining,
                teacher.status
            ])

        return response
    
class MyTeacherProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            teacher = Teacher.objects.get(user=request.user)
            serializer = TeacherSerializer(teacher)
            return Response(serializer.data)
        except Teacher.DoesNotExist:
            return Response({'error': 'Teacher profile not found.'}, status=404)