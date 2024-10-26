from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializer import UserLoginSerializer, UserSignupSerializer, get_token


class UserSignupView(APIView):
    serializer_class = UserSignupSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(
            data={"status": "success", "msg": "User account created."},
            status=status.HTTP_201_CREATED,
        )


class UserLoginView(APIView):
    serializer_class = UserLoginSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data.get("email")
        password = serializer.validated_data.get("password")

        user = authenticate(request, email=email, password=password)

        if not user:
            return Response(
                data={
                    "status": "failed",
                    "msg": "Invalid email and password. Try again",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return Response(
            data={
                "status": "success",
                "msg": "Login successfull",
                "data": get_token(user),
            },
            status=status.HTTP_200_OK,
        )
