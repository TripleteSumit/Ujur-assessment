import re
from django.conf import settings
from django.contrib.auth import password_validation as validator
from django.core import exceptions
from rest_framework import serializers
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User


def get_token(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
        "user_id": user.id,
        "email": user.email,
    }


def is_valid_email(email):
    return re.match(settings.EMAIL, email) is not None


class UserSignupSerializer(serializers.ModelSerializer):
    confirm_password = serializers.CharField(
        write_only=True,
        style={"input_type": "password", "palceholder": "Confirm Password"},
    )
    password = serializers.CharField(
        write_only=True,
        style={"input_type": "password", "placeholder": "Password"},
    )

    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "confirm_password",
        )

    def validate(self, data):
        email = data.get("email")
        password = data.get("password")
        confirm_password = data.pop("confirm_password")

        user = User(**data)

        if not is_valid_email(email):
            serializers.ValidationError("Invalid Email!")
        if password != confirm_password:
            raise serializers.ValidationError(
                {"password": "Confirm password doesn't match."}
            )

        errors = {}

        try:
            validator.validate_password(password=password, user=user)
        except exceptions.ValidationError as e:
            errors["password"] = list(e.messages)

        if errors:
            raise serializers.ValidationError({"error": errors})
        return data

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserLoginSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")

    email = serializers.CharField()
    password = serializers.CharField(
        write_only=True, style={"input_type": "password", "placeholder": "Password"}
    )
