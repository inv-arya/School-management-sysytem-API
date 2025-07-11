from rest_framework.test import APITestCase
from accounts.models import User
from django.urls import reverse
from rest_framework import status

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
