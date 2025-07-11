from django.test import TestCase
from accounts.models import User
from teachers.models import Teacher

class TeacherModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='teacher1', password='pass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.user, first_name='T', last_name='L', email='teacher@example.com', phone_number='0001112222', subject_specialization='History', employee_id='EMP1234', date_of_joining='2021-04-12')

    def test_teacher_str(self):
        self.assertEqual(str(self.teacher), 'T L')
