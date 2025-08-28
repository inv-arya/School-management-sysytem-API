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
    assignment = AssignmentSerializer(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    student_name = serializers.CharField(source='student.get_full_name', read_only=True)
    class Meta:
        model = Submission
        fields = ['id', 'assignment', 'student_name','submission_files', 'submitted_at', 'status', 'status_display', 'submitted_at']
        read_only_fields = ['id', 'student', 'assignment', 'status_display']

class OverdueSubmissionSerializer(serializers.ModelSerializer):
    student = serializers.StringRelatedField()
    assignment = serializers.StringRelatedField()

    class Meta:
        model = Submission
        fields = ['id', 'student', 'assignment', 'status', 'created_at', 'updated_at']  