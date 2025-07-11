# teachers/tests/test_views.py

from rest_framework.test import APITestCase
from rest_framework import status
from accounts.models import User
from teachers.models import Teacher

class TeacherListViewTest(APITestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin',
            password='admin123',
            role='admin',
            is_staff=True  # ensures admin permissions
        )

        # Optionally, create some teacher records to test list response
        Teacher.objects.create(
            user=None,
            first_name='John',
            last_name='Doe',
            email='john.doe@example.com',
            phone_number='1234567890',
            subject_specialization='Mathematics',
            employee_id='EMP001',
            date_of_joining='2022-01-01'
        )

    def test_get_teachers_list_admin(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/teachers/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('John', str(response.data))  # simple check for response content
