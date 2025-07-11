from django.test import TestCase
from accounts.models import User
from teachers.models import Teacher
from students.models import Student
from students.serializers import StudentSerializer

class StudentSerializerTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='studentuser', password='pass', role='student')
        self.teacher = Teacher.objects.create(user=None, first_name='Teacher', last_name='One', email='t1@test.com', phone_number='1234567890', subject_specialization='Science', employee_id='EMP1001', date_of_joining='2020-09-01')
        self.student = Student.objects.create(
            user=self.user,
            first_name='Test',
            last_name='Student',
            email='teststudent@example.com',
            phone_number='9876543210',
            roll_number='REG-2025-1001',
            grade='8',
            date_of_birth='2010-01-01',
            admission_date='2024-06-01',
            status='active',
            assigned_teacher=self.teacher
        )

    def test_student_serialization(self):
        serializer = StudentSerializer(instance=self.student)
        self.assertEqual(serializer.data['first_name'], 'Test')
        self.assertEqual(serializer.data['last_name'], 'Student')
        self.assertEqual(serializer.data['grade'], '8')

    def test_create_student(self):
        user_data = {'username': 'newstud', 'email': 'newstud@example.com', 'password': 'pass123','role': 'student'}
        student_data = {
            'user': user_data,
            'first_name': 'New',
            'last_name': 'Student',
            'email': 'newstud@example.com',
            'phone_number': '1234567890',
            'roll_number': 'REG-2025-2001',
            'grade': '7',
            'date_of_birth': '2011-01-01',
            'admission_date': '2024-01-01',
            'status': 'active',
            'assigned_teacher': self.teacher.pk
        }
        serializer = StudentSerializer(data=student_data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        student = serializer.save()
        self.assertEqual(student.first_name, 'New')
