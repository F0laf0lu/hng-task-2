from rest_framework import serializers, status
from .models import User, Organisation
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["userId", "first_name", "last_name", "email", "phone"]
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["first_name", "last_name", "email", "password", "phone"]


    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        users_org = Organisation.objects.create(
            name=f"{validated_data['first_name']}'s Organization")
        users_org.users.add(user)
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["org_id", "name", "description"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email

        return token