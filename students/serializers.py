from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Student
from teachers.models import Teacher
from accounts.serializers import UserSerializer


class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    assigned_teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), allow_null=True)

    class Meta:
        model = Student
        fields = ['id', 'user', 'first_name', 'last_name', 'email', 'phone_number', 'roll_number', 'grade', 'date_of_birth', 'admission_date', 'status', 'assigned_teacher']

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        return Student.objects.create(user=user, **validated_data)

