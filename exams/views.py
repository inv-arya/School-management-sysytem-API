from rest_framework import generics, permissions,status
from .models import Exam, ExamAttempt
from .serializers import ExamSerializer,ExamStudentListSerializer,ExamAttemptSerializer
from rest_framework.exceptions import PermissionDenied
from students.models import Student
from teachers.models import Teacher
from rest_framework.response import Response


class IsTeacher(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'teacher'
    
class IsStudent(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.role == 'student'

class ExamCreateView(generics.CreateAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def perform_create(self, serializer):
        serializer.save()   

class AvailableExamListView(generics.ListAPIView):
    serializer_class = ExamStudentListSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def get_queryset(self):
        # Get logged in student's instance
        try:
            student = Student.objects.get(user=self.request.user)
        except Student.DoesNotExist:
            raise PermissionDenied("Student profile not found.")

        # Get teacher assigned to the student
        assigned_teacher = student.assigned_teacher

        # Get all exams created by that teacher
        all_teacher_exams = Exam.objects.filter(created_by=assigned_teacher)

        # Filter out exams already attempted by the student
        attempted_exam_ids = ExamAttempt.objects.filter(student=student).values_list('exam_id', flat=True)
        available_exams = all_teacher_exams.exclude(id__in=attempted_exam_ids)

        return available_exams
class MyExamsView(generics.ListAPIView):
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsTeacher]

    def get_queryset(self):
        try:
            teacher = Teacher.objects.get(user=self.request.user)
        except Teacher.DoesNotExist:
            raise PermissionDenied("Teacher profile not found.")

        return Exam.objects.filter(created_by=teacher)
    
class AttemptExamView(generics.CreateAPIView):
    serializer_class = ExamAttemptSerializer
    permission_classes = [permissions.IsAuthenticated, IsStudent]

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        return Response({"message": "Exam submitted successfully!"}, status=status.HTTP_201_CREATED)
