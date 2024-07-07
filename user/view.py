from rest_framework.response import Response
from rest_framework import status, serializers
from rest_framework.generics import CreateAPIView
from .serializers import RegisterSerializer, UserSerializer

# Create your views here.

class RegisterView(CreateAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            required_fields = ["first_name", "last_name", "email", "password", "phone"]
            missing_fields = [field for field in required_fields if not serializer.data.get(field)]
            e.detail = []
            for field in missing_fields:
                e.detail.append({
                    "field":field,
                    "message":"This field cannot be blank"
                })
            return Response({"errors": e.detail}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        return super().post(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        try:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            # self.perform_create(serializer)
            print(serializer.validated_data)
        except Exception as e:
            fail_response = {
                    "status": "Bad request",
                    "message": "Registration unsuccessful",
                    "statusCode": 400
                }
            return Response(fail_response, status=status.HTTP_400_BAD_REQUEST)
        headers = self.get_success_headers(serializer.data)
        success_response = {
            "status": "success",
            "message": "Registration successful",
            "data": {
                    "accessToken": "",
                    "user": {}
                }
            }
        return Response(success_response, status=status.HTTP_201_CREATED, headers=headers)
    

class LoginView():
    pass
