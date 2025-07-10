from rest_framework import serializers
from .models import Teacher
from students.serializers import StudentSerializer

class TeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = '__all__'

class TeacherStudentListSerializer(serializers.ModelSerializer):
    students = StudentSerializer(many=True, read_only=True)

    class Meta:
        model = Teacher
        fields = ['id', 'user', 'students']