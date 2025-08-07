from django.db import models
import uuid
from teachers.models import Teacher
from students.models import Student

class ChatRequest(models.Model):
    STATUS_PENDING = 0
    STATUS_APPROVED = 1
    STATUS_CANCELLED = 2

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_APPROVED, 'Approved'),
        (STATUS_CANCELLED, 'Cancelled'),
    ]

    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    student = models.ForeignKey(Student, on_delete=models.CASCADE)
    status = models.IntegerField(choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    approval_token = models.UUIDField(default=uuid.uuid4, unique=True)

    class Meta:
        unique_together = ('teacher', 'student')

    def __str__(self):
        return f"{self.teacher} ↔ {self.student} ({self.get_status_display()})"

class ChatMessage(models.Model):
    SENDER_TEACHER = 0
    SENDER_STUDENT = 1

    SENDER_CHOICES = [
        (SENDER_TEACHER, 'Teacher'),
        (SENDER_STUDENT, 'Student'),
    ]

    chat_request = models.ForeignKey(ChatRequest, on_delete=models.CASCADE, related_name='messages')
    sender_type = models.IntegerField(choices=SENDER_CHOICES)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_sender_type_display()}: {self.message[:30]}"
