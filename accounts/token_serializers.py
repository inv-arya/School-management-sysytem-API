from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.exceptions import AuthenticationFailed
from teachers.models import Teacher
from students.models import Student
class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        token['role'] = user.role
        token['username'] = user.username
        return token

    def validate(self, attrs):
        data = super().validate(attrs)
        if self.user.role == "teacher":
            try:
                teacher = Teacher.objects.get(user=self.user)
                if teacher.status.lower() != "active":
                    raise AuthenticationFailed("Your account has been restricted. Please contact admin.")
            except Teacher.DoesNotExist:
                raise AuthenticationFailed("Teacher profile not found.")

        elif self.user.role == "student":
            try:
                student = Student.objects.get(user=self.user)
                if student.status.lower() != "active":
                    raise AuthenticationFailed("Your account has been restricted. Please contact admin.")
            except Student.DoesNotExist:
                raise AuthenticationFailed("Student profile not found.")
        data['username'] = self.user.username
        data['role'] = self.user.role
        return data
