from rest_framework.test import APITestCase
from accounts.models import User
from django.urls import reverse
from rest_framework import status

class AuthTestCase(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass', role='student')

    def test_token_obtain_success(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'testuser', 'password': 'testpass'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_token_obtain_fail(self):
        url = reverse('token_obtain_pair')
        response = self.client.post(url, {'username': 'testuser', 'password': 'wrongpass'})
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
