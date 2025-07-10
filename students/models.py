from django.db import models
from teachers.models import Teacher
from django.conf import settings


class Student(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
    ]
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15)
    roll_number = models.CharField(max_length=20, unique=True)
    grade = models.CharField(max_length=10)
    date_of_birth = models.DateField()
    admission_date = models.DateField()
    status = models.CharField(max_length=8, choices=STATUS_CHOICES, default='active')
    assigned_teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True, related_name='students')

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

