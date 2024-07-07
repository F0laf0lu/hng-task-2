from django.test import TestCase
from rest_framework.test import APIClient
from django.urls import reverse
from django.contrib.auth import get_user_model
from user.models import Organisation

User = get_user_model()

class OrganisationAccessTest(TestCase):
    
    def setUp(self):
        self.client = APIClient()
        self.user1 = User.objects.create_user(
            email='user1@example.com',
            first_name='User1',
            last_name='Test',
            password='password123'
        )
        self.user2 = User.objects.create_user(
            email='user2@example.com',
            first_name='User2',
            last_name='Test',
            password='password123'
        )
        self.org1 = Organisation.objects.create(name="User1's Organisation")
        self.org1.users.add(self.user1)

    def test_organisation_access_forbidden(self):
        # self.client.force_authenticate(user=self.user2)
        response = self.client.get(reverse('organisation_detail', kwargs={'org_id': self.org1.org_id}))
        self.assertEqual(response.status_code, 401)

    def test_organisation_access_allowed(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(reverse('organisation_detail', kwargs={'org_id': self.org1.org_id}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['name'], "User1's Organisation")
