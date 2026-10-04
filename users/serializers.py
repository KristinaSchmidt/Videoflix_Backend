from rest_framework import serializers

from .models import User


class RegistrationSerializer(serializers.ModelSerializer):
    """Validate registration data and create a new inactive user."""

    confirmed_password = serializers.CharField(write_only=True)

    class Meta:
        """Configure fields used during user registration."""

        model = User
        fields = ("email", "password", "confirmed_password")
        extra_kwargs = {
            "password": {"write_only": True},
        }

    def validate(self, data):
        """Ensure that password and password confirmation match."""
        if data["password"] != data["confirmed_password"]:
            raise serializers.ValidationError(
                {"password": "Passwords do not match."}
            )

        return data

    def create(self, validated_data):
        """Create an inactive user until the account is activated."""
        validated_data.pop("confirmed_password")

        return User.objects.create_user(
            is_active=False,
            **validated_data,
        )