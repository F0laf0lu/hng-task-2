from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import status, serializers, permissions
from rest_framework.views import APIView
from django.contrib.auth import authenticate
from rest_framework.generics import CreateAPIView, ListAPIView, RetrieveAPIView, ListCreateAPIView
from .serializers import CustomTokenObtainPairSerializer, RegisterSerializer, OrganizationSerializer, UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import Organisation, User

# Create your views here.

class RegisterView(CreateAPIView):
    permission_classes = [permissions.AllowAny]
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            success_response = {
                "status": "success",
                "message": "Registration successful",
                "data": {
                    "accessToken": str(refresh.access_token),
                    "user": UserSerializer(user).data
                }
            }
            return Response(success_response, status=status.HTTP_201_CREATED)
        
        required_fields = ["firstName", "lastName", "email", "password"]
        missing_fields = [field for field in required_fields if not serializer.initial_data.get(field)]
        if missing_fields:
            error_detail = [{"field": field, "message": "This field cannot be blank"} for field in missing_fields]
            return Response({"errors": error_detail}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    def post(self, request):
        email = request.data.get('email')
        password = request.data.get('password')
        user = authenticate(email=email, password=password)

        if user is not None:
            token_serializer = CustomTokenObtainPairSerializer()
            tokens = token_serializer.get_token(user)
            return Response({
                "status": "success",
                "message": "Login successful",
                "data": {
                    "accessToken": str(tokens.access_token),
                    "user": UserSerializer(user).data
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response({"status": "Bad request", "message": "Authentication failed", "statusCode": 401}, status=status.HTTP_401_UNAUTHORIZED)
        

class OrganizationListview(ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Organisation.objects.all()
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        user = self.request.user
        return user.organisations.all()
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        res = {
                "status": "success",
                    "message": "user organisations",
                "data": {
                "organisations": serializer.data
                }
            }
        return Response(res)

    def post(self, request):
        data = request.data
        if not data.get('name'):
            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)
        try:
            org = Organisation.objects.create(name=data['name'], description=data.get('description'))
            org.users.add(request.user)
            return Response({
                "status": "success",
                "message": "Organisation created successfully",
                "data": OrganizationSerializer(org).data
            }, status=status.HTTP_201_CREATED)
        except Exception as e:
            return Response({
                "status": "Bad Request",
                "message": "Client error",
                "statusCode": 400
            }, status=status.HTTP_400_BAD_REQUEST)

class OrganizationDetailView(RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Organisation.objects.all()
    serializer_class = OrganizationSerializer
    lookup_field = "orgId"

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        res = {
                "status": "success",
                    "message": "Organization detail",
                "data": serializer.data
            }
        return Response(res)
    

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, *args, **kwargs):
        user = self.request.user 
        user_id = kwargs.get('pk') 
        try:
            user_instance = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response({
                "status": "error",
                "message": "User does not exist"
            }, status=status.HTTP_404_NOT_FOUND)

        if user == user_instance or user.is_superuser:
            serializer = UserSerializer(user_instance)
            return Response({
                "status": "success",
                "message": "User details retrieved successfully",
                "data": {
                    "userId": str(user_instance.id),
                    "firstName": user_instance.firstName,
                    "lastName": user_instance.lastName,
                    "email": user_instance.email,
                    "phone": user_instance.phone
                }
            }, status=status.HTTP_200_OK)
        else:
            user_orgs = Organisation.objects.filter(users=user)
            user_instance_orgs = Organisation.objects.filter(users=user_instance)
            
            common_orgs = user_orgs.intersection(user_instance_orgs)
            if common_orgs.exists():
                serializer = UserSerializer(user_instance)
                return Response({
                    "status": "success",
                    "message": "User details retrieved successfully",
                    "data": serializer.data
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "status": "error",
                    "message": "Unauthorized access to user details"
                }, status=status.HTTP_403_FORBIDDEN)


class AddUserToOrganisationView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def post(self, request, orgId):
        org = get_object_or_404(Organisation, orgId=orgId)
        
        if request.user not in org.users.all():
            return Response({
                "status": "error",
                "message": "You do not have permission to add users to this organisation."
            }, status=status.HTTP_403_FORBIDDEN)
        user_id = request.data.get('userId')
        user = get_object_or_404(User, userId=user_id)
        org.users.add(user)
        return Response({
            "status": "success",
            "message": "User added to organisation successfully"
        }, status=status.HTTP_200_OK)