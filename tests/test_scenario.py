from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Organisation

User = get_user_model()

class UserRegistrationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_successful_registration_with_default_organisation(self):
        payload = {
            'first_name': 'John',
            'last_name': 'Doe',
            'email': 'johndoe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data['status'], 'success')

        user = User.objects.get(email='johndoe@example.com')
        self.assertIsNotNone(user)

        organisation = Organisation.objects.get(users=user)
        self.assertEqual(organisation.name, "John's Organization")

        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'johndoe@example.com')

class UserLoginTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.login_url = reverse('login')
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )

    def test_successful_login(self):
        payload = {
            'email': 'testuser@example.com',
            'password': 'password123'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['status'], 'success')
        self.assertIn('accessToken', response.data['data'])
        self.assertEqual(response.data['data']['user']['email'], 'testuser@example.com')

    def test_unsuccessful_login(self):
        payload = {
            'email': 'testuser@example.com',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, payload, format='json')
        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.data['status'], 'Bad request')
        self.assertEqual(response.data['message'], 'Authentication failed')

class MissingFieldsTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')

    def test_missing_first_name(self):
        payload = {
            'last_name': 'Doe',
            'email': 'janedoe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)

    def test_missing_last_name(self):
        payload = {
            'first_name': 'Jane',
            'email': 'janedoe@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)

    def test_missing_email(self):
        payload = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)

    def test_missing_password(self):
        payload = {
            'first_name': 'Jane',
            'last_name': 'Doe',
            'email': 'janedoe@example.com',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)

class DuplicateUserTest(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        User.objects.create_user(
            email='existinguser@example.com',
            first_name='Existing',
            last_name='User',
            password='password123'
        )

    def test_duplicate_email(self):
        payload = {
            'first_name': 'New',
            'last_name': 'User',
            'email': 'existinguser@example.com',
            'password': 'password123',
            'phone': '1234567890'
        }
        response = self.client.post(self.register_url, payload, format='json')
        self.assertEqual(response.status_code, 422)
        self.assertIn('errors', response.data)