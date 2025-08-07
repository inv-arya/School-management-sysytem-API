from rest_framework import generics, permissions,status
from .models import Exam, ExamAttempt
from .serializers import ExamSerializer,AvailableExamSerializer,ExamAttemptSerializer
from rest_framework.exceptions import PermissionDenied
from students.models import Student
from teachers.models import Teacher
from rest_framework.response import Response


class IsExamOwnerTeacher(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        
        if request.method in permissions.SAFE_METHODS:
            return True
        
        
        return (
            request.user.role == 'teacher' and
            hasattr(request.user, 'teacher') and
            obj.created_by == request.user.teacher
        )

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
    serializer_class = AvailableExamSerializer
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
        serializer = self.get_serializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        attempt = serializer.save()

        return Response({
            "message": "Exam submitted successfully!",
            "score": attempt.score,
            "correct_answers": attempt.correct_answers,
            "total_questions": attempt.total_questions
        }, status=status.HTTP_201_CREATED)


class ExamDetailDeleteView(generics.RetrieveDestroyAPIView):
    queryset = Exam.objects.all()
    serializer_class = ExamSerializer
    permission_classes = [permissions.IsAuthenticated, IsExamOwnerTeacher]

    def get_object(self):
        exam = super().get_object()
        user = self.request.user

       
        if user.role == 'student':
            student = getattr(user, 'student', None)
            if not student:
                raise PermissionDenied("Student profile not found.")
            assigned_teacher = student.assigned_teacher
            if exam.created_by != assigned_teacher:
                raise PermissionDenied("You don't have permission to view this exam.")
        
        
        return exam