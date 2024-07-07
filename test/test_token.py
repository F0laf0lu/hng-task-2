from django.test import TestCase
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from django.utils import timezone
from datetime import timedelta
from user.serializers import CustomTokenObtainPairSerializer

User = get_user_model()

class TokenGenerationTest(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@example.com',
            first_name='Test',
            last_name='User',
            password='password123'
        )
        self.token = CustomTokenObtainPairSerializer.get_token(self.user)

    def test_token_generation(self):
        token = self.token.access_token
        self.assertEqual(token['user_id'], self.user.id)
        self.assertEqual(token['email'], self.user.email)

    def test_token_expiration(self):
        token = AccessToken.for_user(self.user)
        expiration_time = timezone.now() + timedelta(minutes=30)
        self.assertLessEqual(token['exp'], int(expiration_time.timestamp()))
