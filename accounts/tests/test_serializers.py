from django.test import TestCase
from accounts.models import User
from accounts.serializers import UserSerializer

class UserSerializerTest(TestCase):
    def test_serialize(self):
        user = User.objects.create_user(username='serialuser', password='pass', role='student')
        serializer = UserSerializer(user)
        self.assertEqual(serializer.data['username'], 'serialuser')
        self.assertEqual(serializer.data['role'], 'student')

    def test_create(self):
        data = {'username': 'newuser', 'password': 'newpass', 'role': 'teacher'}
        serializer = UserSerializer(data=data)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertEqual(user.username, 'newuser')
        self.assertTrue(user.check_password('newpass'))

    def test_update_password(self):
        user = User.objects.create_user(username='updateuser', password='oldpass', role='student')
        serializer = UserSerializer(user, data={'password': 'newpass'}, partial=True)
        self.assertTrue(serializer.is_valid(), serializer.errors)
        user = serializer.save()
        self.assertTrue(user.check_password('newpass'))
