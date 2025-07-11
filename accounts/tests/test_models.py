from django.test import TestCase
from accounts.models import User

class UserModelTest(TestCase):
    def test_create_user(self):
        user = User.objects.create_user(username='user1', password='pass', role='teacher')
        self.assertEqual(user.username, 'user1')
        self.assertEqual(user.role, 'teacher')
        self.assertTrue(user.check_password('pass'))
