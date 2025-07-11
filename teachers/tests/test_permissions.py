from rest_framework.test import APITestCase
from accounts.models import User

class TeacherPermissionTest(APITestCase):
    def setUp(self):
        self.teacher = User.objects.create_user(username='teacher', password='pass', role='teacher')

    def test_teacher_role(self):
        self.assertEqual(self.teacher.role, 'teacher')
