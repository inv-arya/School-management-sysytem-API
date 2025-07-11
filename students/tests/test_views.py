from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from students.models import Student
from teachers.models import Teacher

class StudentListViewTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(username='admin', password='adminpass', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher', password='teachpass', role='teacher')
        self.teacher = Teacher.objects.create(user=self.teacher_user, first_name='T', last_name='L', email='t@example.com', phone_number='123', subject_specialization='Math', employee_id='EMP001', date_of_joining='2020-01-01')

        self.student = Student.objects.create(user=None, first_name='Stu', last_name='D', email='stu@example.com', phone_number='555', roll_number='REG-001', grade='10', date_of_birth='2010-01-01', admission_date='2020-01-01', status='active', assigned_teacher=self.teacher)

    def test_list_students_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_list_students_teacher(self):
        self.client.force_authenticate(user=self.teacher_user)
        response = self.client.get('/api/students/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_student_admin(self):
        self.client.force_authenticate(user=self.admin)
        data = {
            "user": {
                "username": "newstudent",
                "email": "newstud@example.com",
                "password": "newpass123",
                "role": "student"
            },
            "first_name": "New",
            "last_name": "Student",
            "email": "newstud@example.com",
            "phone_number": "1234567890",
            "roll_number": "REG-2025-9999",
            "grade": "9",
            "date_of_birth": "2010-01-01",
            "admission_date": "2024-01-01",
            "status": "active",
            "assigned_teacher": self.teacher.pk
        }
        response = self.client.post('/api/students/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
