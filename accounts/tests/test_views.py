from rest_framework.test import APITestCase
from accounts.models import User
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

class ProfileViewTest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='viewuser', password='testpass', role='student')

    def test_get_profile_authenticated(self):
        self.client.force_authenticate(user=self.user)
        url = reverse('my_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], 'viewuser')

    def test_get_profile_unauthenticated(self):
        url = reverse('my_profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PasswordResetViewTests(APITestCase):
    def setUp(self):
        self.client = APIClient()
        self.reset_url = reverse('password_reset_request')

        # Create a test user
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@example.com',
            password='testpass123'
        )

    def test_valid_password_reset_request(self):
        response = self.client.post(self.reset_url, {'email': 'testuser@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        self.assertEqual(response.data['message'], 'Password reset email sent if email exists.')

    def test_password_reset_request_with_unregistered_email(self):
        response = self.client.post(self.reset_url, {'email': 'unknown@example.com'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)

    def test_password_reset_request_without_email(self):
        response = self.client.post(self.reset_url, {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('error', response.data)
        self.assertEqual(response.data['error'], 'Email is required')