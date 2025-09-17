from rest_framework import serializers
from .models import Assignment
from .models import Submission
from django.utils import timezone

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'subject', 'grade', 'deadline', 'max_marks', 'reference_files', 'created_by', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_by', 'created_at', 'updated_at']

class StudentAssignmentSerializer(serializers.ModelSerializer):
    status = serializers.SerializerMethodField()
    status_display = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = ['id', 'title', 'description', 'subject', 'grade', 'deadline', 'max_marks', 'reference_files', 'status', 'status_display', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']

    def get_status(self, obj):
        student = self.context['student']
        submission, _ = Submission.objects.get_or_create(
            student=student,
            assignment=obj,
            defaults={'status': 0}
        )
        if submission.status != 1 and obj.deadline < timezone.now():
            submission.status = 2
            submission.save()
        return submission.status

    def get_status_display(self, obj):
        student = self.context['student']
        submission, _ = Submission.objects.get_or_create(
            student=student,
            assignment=obj,
            defaults={'status': 0}
        )
        if submission.status != 1 and obj.deadline < timezone.now():
            submission.status = 2
            submission.save()
        return submission.get_status_display()

class SubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Submission
        fields = ['id', 'student_name', 'submission_files', 'submitted_at', 'status', 'status_display','marks']
        read_only_fields = ['id', 'student_name', 'status', 'status_display', 'submitted_at']

    def get_student_name(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return "Unknown Student"

class OverdueSubmissionSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()

    class Meta:
        model = Submission
        fields = ['student_name']

    def get_student_name(self, obj):
        if obj.student:
            return f"{obj.student.first_name} {obj.student.last_name}"
        return "Unknown Student"