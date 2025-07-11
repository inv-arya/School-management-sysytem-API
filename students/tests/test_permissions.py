from rest_framework.test import APITestCase, APIRequestFactory
from accounts.models import User
from students.models import Student
from teachers.models import Teacher
from accounts.permissions import StudentAccessPermission


class StudentAccessPermissionTestCase(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()

        # Admin user
        self.admin_user = User.objects.create_user(username='admin', password='adminpass', role='admin')

        # Teacher with assigned student
        self.teacher_user = User.objects.create_user(username='teacher1', password='teacherpass', role='teacher')
        self.teacher = Teacher.objects.create(
            user=self.teacher_user,
            first_name='Teacher',
            last_name='One',
            email='teacher1@example.com',
            phone_number='1234567890',
            subject_specialization='Math',
            employee_id='EMP001',
            date_of_joining='2020-01-01'
        )

        # Another teacher
        self.other_teacher_user = User.objects.create_user(username='teacher2', password='pass', role='teacher')
        self.other_teacher = Teacher.objects.create(
            user=self.other_teacher_user,
            first_name='Other',
            last_name='Teacher',
            email='other@example.com',
            phone_number='0000000000',
            subject_specialization='Physics',
            employee_id='EMP002',
            date_of_joining='2021-02-01'
        )

        # Student assigned to teacher
        self.student_user = User.objects.create_user(username='student', password='studentpass', role='student')
        self.student = Student.objects.create(
            user=self.student_user,
            first_name='Student',
            last_name='One',
            email='student1@example.com',
            phone_number='1112223333',
            roll_number='REG-2025-0001',
            grade='10',
            date_of_birth='2009-05-10',
            admission_date='2023-06-01',
            status='active',
            assigned_teacher=self.teacher
        )

        # Another student
        self.other_student_user = User.objects.create_user(username='student2', password='studentpass', role='student')
        self.other_student = Student.objects.create(
            user=self.other_student_user,
            first_name='Student2',
            last_name='Two',
            email='student2@example.com',
            phone_number='4445556666',
            roll_number='REG-2025-0002',
            grade='10',
            date_of_birth='2009-06-10',
            admission_date='2023-07-01',
            status='active',
            assigned_teacher=self.other_teacher
        )

    def test_admin_has_permission(self):
        request = self.factory.get('/')
        request.user = self.admin_user
        permission = StudentAccessPermission()
        self.assertTrue(permission.has_object_permission(request, None, self.student))

    def test_teacher_has_permission_for_assigned_student(self):
        request = self.factory.get('/')
        request.user = self.teacher_user
        permission = StudentAccessPermission()
        self.assertTrue(permission.has_object_permission(request, None, self.student))

    def test_teacher_denied_for_unassigned_student(self):
        request = self.factory.get('/')
        request.user = self.teacher_user
        permission = StudentAccessPermission()
        self.assertFalse(permission.has_object_permission(request, None, self.other_student))

    def test_student_has_read_permission_for_self(self):
        request = self.factory.get('/')
        request.method = 'GET'
        request.user = self.student_user
        permission = StudentAccessPermission()
        self.assertTrue(permission.has_object_permission(request, None, self.student))

    def test_student_denied_for_others(self):
        request = self.factory.get('/')
        request.method = 'GET'
        request.user = self.student_user
        permission = StudentAccessPermission()
        self.assertFalse(permission.has_object_permission(request, None, self.other_student))

    def test_student_denied_for_write_methods(self):
        request = self.factory.put('/')
        request.user = self.student_user
        permission = StudentAccessPermission()
        self.assertFalse(permission.has_object_permission(request, None, self.student))
