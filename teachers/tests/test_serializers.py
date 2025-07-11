from django.test import TestCase
from accounts.models import User
from teachers.models import Teacher
from teachers.serializers import TeacherSerializer

class TeacherSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teachuser', password='pass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.user, first_name='A', last_name='B', email='ab@example.com', phone_number='1112223333', subject_specialization='Geo', employee_id='EMP9999', date_of_joining='2019-11-11')

    def test_teacher_serialization(self):
        serializer = TeacherSerializer(instance=self.teacher)
        self.assertEqual(serializer.data['first_name'], 'A')
        self.assertEqual(serializer.data['last_name'], 'B')
