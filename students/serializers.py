
from rest_framework import serializers  
from .models import Student
from teachers.models import Teacher
from accounts.serializers import UserSerializer

class StudentSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    assigned_teacher = serializers.PrimaryKeyRelatedField(queryset=Teacher.objects.all(), allow_null=True)

    class Meta:
        model = Student
        fields = [
            'id', 'user', 'first_name', 'last_name', 'email',
            'phone_number', 'roll_number', 'grade',
            'date_of_birth', 'admission_date', 'status', 'assigned_teacher'
        ]



    def validate_email(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.email == value:
            return value
        if Student.objects.filter(email=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError("student with this email already exists.")
        return value

    def validate_roll_number(self, value):
        instance = getattr(self, 'instance', None)
        if instance and instance.roll_number == value:
            return value
        if Student.objects.filter(roll_number=value).exclude(pk=getattr(self.instance, 'pk', None)).exists():
            raise serializers.ValidationError("student with this roll number already exists.")
        return value

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = UserSerializer().create(user_data)
        return Student.objects.create(user=user, **validated_data)

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        if user_data:
            user_serializer = UserSerializer(instance=instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        return instance
