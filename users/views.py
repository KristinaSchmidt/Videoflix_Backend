from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import RegistrationSerializer
from .utils import send_activation_email


class RegisterView(APIView):
    """Handle the registration of new Videoflix users."""

    authentication_classes = []
    permission_classes = []

    def post(self, request):
        """Create an inactive user and send an activation email."""
        serializer = RegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        send_activation_email(user)

        return Response(
            {
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
                "message": "Registration successful. Please check your email.",
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """Activate a registered account using its UID and activation token."""

    authentication_classes = []
    permission_classes = []

    def get(self, request, uidb64, token):
        """Validate the activation link and activate the user account."""
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response(
                {"message": "Account activation failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"message": "Account activation failed."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.is_active = True
        user.save(update_fields=["is_active"])

        return Response(
            {"message": "Account successfully activated."},
            status=status.HTTP_200_OK,
        )