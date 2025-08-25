from django.db import models
from django.conf import settings
from teachers.models import Teacher
from students.models import Student

class Assignment(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    subject = models.CharField(max_length=100)
    grade = models.CharField(max_length=10)  
    deadline = models.DateTimeField()
    max_marks = models.FloatField()
    reference_files = models.FileField(upload_to='assignments/references/%Y/%m/%d/', blank=True, null=True)
    created_by = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='assignments')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions')
    submission_files = models.FileField(upload_to='assignments/submissions/%Y/%m/%d/')
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.FloatField(blank=True, null=True)

    class Meta:
        unique_together = ('assignment', 'student')

    def __str__(self):
        return f"{self.student} - {self.assignment}"