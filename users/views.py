
from django.contrib.auth import authenticate
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from rest_framework import status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models import User
from .serializers import (
    LoginSerializer,
    PasswordConfirmSerializer,
    PasswordResetSerializer,
    RegistrationSerializer,
)
from .utils import send_activation_email, send_password_reset_email


def set_auth_cookies(response, refresh):
    """Store access and refresh tokens in HTTP-only cookies."""
    response.set_cookie(
        key="access_token",
        value=str(refresh.access_token),
        httponly=True,
        secure=False,
        samesite="Lax",
    )
    response.set_cookie(
        key="refresh_token",
        value=str(refresh),
        httponly=True,
        secure=False,
        samesite="Lax",
    )


class RegisterView(APIView):
    """Register new users without requiring an existing JWT."""

    authentication_classes = []
    permission_classes = [AllowAny]

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
                "message": (
                    "Registration successful. "
                    "Please check your email."
                ),
            },
            status=status.HTTP_201_CREATED,
        )


class ActivateAccountView(APIView):
    """Activate an account using its UID and activation token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def get(self, request, uidb64, token):
        """Validate the activation link and activate the account."""
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
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


class LoginView(APIView):
    """Authenticate users and create JWT authentication cookies."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate credentials and create access and refresh tokens."""
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = authenticate(
            request=request,
            email=serializer.validated_data["email"],
            password=serializer.validated_data["password"],
        )

        if user is None:
            return Response(
                {"detail": "Invalid email or password."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "detail": "Login successful.",
                "user": {
                    "id": user.id,
                    "email": user.email,
                },
            },
            status=status.HTTP_200_OK,
        )

        set_auth_cookies(response, refresh)

        return response


class LogoutView(APIView):
    """Log out a user and remove authentication cookies."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Blacklist the refresh token and remove JWT cookies."""
        refresh_token = request.COOKIES.get("refresh_token")

        if refresh_token:
            try:
                RefreshToken(refresh_token).blacklist()
            except Exception:
                pass

        response = Response(
            {"detail": "Logout successful."},
            status=status.HTTP_200_OK,
        )

        response.delete_cookie("access_token")
        response.delete_cookie("refresh_token")

        return response


class TokenRefreshView(APIView):
    """Create a new access token from the refresh cookie."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Validate the refresh token and create a new access token."""
        refresh_token = request.COOKIES.get("refresh_token")

        if not refresh_token:
            return Response(
                {"detail": "Refresh token missing."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        try:
            refresh = RefreshToken(refresh_token)
            access_token = str(refresh.access_token)
        except Exception:
            return Response(
                {"detail": "Invalid refresh token."},
                status=status.HTTP_401_UNAUTHORIZED,
            )

        response = Response(
            {"detail": "Token refreshed."},
            status=status.HTTP_200_OK,
        )

        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=False,
            samesite="Lax",
        )

        return response


class PasswordResetView(APIView):
    """Start the password reset process."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request):
        """Send a reset email without exposing whether a user exists."""
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = None

        if user:
            send_password_reset_email(user)

        return Response(
            {
                "detail": (
                    "If an account exists for this email, "
                    "a reset link has been sent."
                )
            },
            status=status.HTTP_200_OK,
        )


class PasswordConfirmView(APIView):
    """Set a new password using a valid UID and reset token."""

    authentication_classes = []
    permission_classes = [AllowAny]

    def post(self, request, uidb64, token):
        """Validate the reset token and save the new password."""
        serializer = PasswordConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)
        except (
            TypeError,
            ValueError,
            OverflowError,
            User.DoesNotExist,
        ):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not default_token_generator.check_token(user, token):
            return Response(
                {"detail": "Invalid password reset link."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        user.set_password(
            serializer.validated_data["new_password"]
        )
        user.save(update_fields=["password"])

        return Response(
            {"detail": "Password successfully changed."},
            status=status.HTTP_200_OK,
        )
