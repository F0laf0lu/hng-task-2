from rest_framework import serializers, status
from .models import User, Organisation
from django.contrib.auth import get_user_model
from rest_framework.exceptions import ValidationError
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["userId", "firstName", "lastName", "email", "phone"]
    
class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["firstName", "lastName", "email", "password", "phone"]

    def validate(self, data):
        # Custom validation for required fields
        required_fields = ["firstName", "lastName", "email", "password"]
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            error_detail = [{"field": field, "message": "This field cannot be blank"} for field in missing_fields]
            raise ValidationError({"errors": error_detail}, code=422)

        return data

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        users_org = Organisation.objects.create(
            name=f"{validated_data['firstName']}'s Organization")
        users_org.users.add(user)
        return user

class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organisation
        fields = ["orgId", "name", "description"]


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Add custom claims
        token['email'] = user.email

        return token