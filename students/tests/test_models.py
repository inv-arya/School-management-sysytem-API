from django.test import TestCase
from students.models import Student
from accounts.models import User
from teachers.models import Teacher

class StudentModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='student1', password='pass', role='student')
        self.teacher = Teacher.objects.create(user=None, first_name='T1', last_name='L1', email='t1@example.com', phone_number='1234567890', subject_specialization='Math', employee_id='EMP001', date_of_joining='2020-01-01')
        self.student = Student.objects.create(
            user=self.user,
            first_name='John',
            last_name='Doe',
            email='john@example.com',
            phone_number='9999999999',
            roll_number='REG-2025-001',
            grade='10',
            date_of_birth='2008-05-10',
            admission_date='2023-06-01',
            status='active',
            assigned_teacher=self.teacher
        )

    def test_str(self):
        self.assertEqual(str(self.student), 'John Doe')
