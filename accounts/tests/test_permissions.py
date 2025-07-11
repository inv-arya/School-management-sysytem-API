from rest_framework.test import APIRequestFactory, APITestCase
from accounts.models import User
from accounts.permissions import StudentAccessPermission
from students.models import Student
from teachers.models import Teacher

class StudentAccessPermissionTest(APITestCase):
    def setUp(self):
        self.factory = APIRequestFactory()
        self.admin = User.objects.create_user(username='admin', password='adminpass', role='admin')
        self.teacher_user = User.objects.create_user(username='teacher', password='teachpass', role='teacher')
        self.student_user = User.objects.create_user(username='student', password='studpass', role='student')
        self.teacher = Teacher.objects.create(user=self.teacher_user, first_name='T', last_name='L', email='t@example.com', phone_number='123', subject_specialization='Math', employee_id='EMP001', date_of_joining='2020-01-01')
        self.student = Student.objects.create(user=self.student_user, first_name='S', last_name='L', email='s@example.com', phone_number='456', roll_number='REG-001', grade='10', date_of_birth='2010-01-01', admission_date='2020-06-01', status='active', assigned_teacher=self.teacher)

    def test_admin_has_access(self):
        request = self.factory.get('/')
        request.user = self.admin
        perm = StudentAccessPermission()
        self.assertTrue(perm.has_object_permission(request, None, self.student))

    def test_teacher_has_access_if_assigned(self):
        request = self.factory.get('/')
        request.user = self.teacher_user
        perm = StudentAccessPermission()
        self.assertTrue(perm.has_object_permission(request, None, self.student))

    def test_teacher_no_access_if_not_assigned(self):
        other_teacher_user = User.objects.create_user(username='teacher2', password='pass', role='teacher')
        request = self.factory.get('/')
        request.user = other_teacher_user
        perm = StudentAccessPermission()
        self.assertFalse(perm.has_object_permission(request, None, self.student))

    def test_student_can_read_own_record(self):
        request = self.factory.get('/')
        request.user = self.student_user
        perm = StudentAccessPermission()
        self.assertTrue(perm.has_object_permission(request, None, self.student))

    def test_student_cannot_modify(self):
        request = self.factory.post('/')
        request.user = self.student_user
        perm = StudentAccessPermission()
        self.assertFalse(perm.has_object_permission(request, None, self.student))
