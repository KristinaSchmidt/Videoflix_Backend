"""Tests for Videoflix authentication endpoints."""

from unittest.mock import patch

from django.contrib.auth.tokens import default_token_generator
from django.test import TestCase
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from rest_framework.test import APIClient

from .models import User


class AuthenticationTests(TestCase):
    """Test registration, activation and JWT authentication."""

    def setUp(self):
        """Create an API client used by all authentication tests."""
        self.client = APIClient()
        self.email = "test@example.com"
        self.password = "TestPassword123!"

    @patch("users.views.send_activation_email")
    def test_registration_creates_inactive_user(self, mocked_email):
        """Registration should create an inactive user."""
        response = self.client.post(
            "/api/register/",
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 201)

        user = User.objects.get(email=self.email)

        self.assertFalse(user.is_active)
        self.assertTrue(user.check_password(self.password))
        mocked_email.assert_called_once_with(user)

    def test_registration_rejects_different_passwords(self):
        """Registration should reject passwords that do not match."""
        response = self.client.post(
            "/api/register/",
            {
                "email": self.email,
                "password": self.password,
                "confirmed_password": "DifferentPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 400)
        self.assertFalse(
            User.objects.filter(email=self.email).exists()
        )

    def test_account_activation(self):
        """A valid activation token should activate the user."""
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=False,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        response = self.client.get(
            f"/api/activate/{uid}/{token}/"
        )

        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.is_active)

    def test_login_sets_authentication_cookies(self):
        """A valid login should set access and refresh cookies."""
        User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        response = self.client.post(
            "/api/login/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)
        self.assertIn("refresh_token", response.cookies)

    def test_invalid_login_returns_generic_error(self):
        """Invalid credentials should not expose account information."""
        response = self.client.post(
            "/api/login/",
            {
                "email": "unknown@example.com",
                "password": "WrongPassword123!",
            },
            format="json",
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.data["detail"],
            "Invalid email or password.",
        )

    def test_token_refresh_creates_new_access_cookie(self):
        """A refresh token should create a new access token."""
        User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        login_response = self.client.post(
            "/api/login/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        self.assertEqual(login_response.status_code, 200)

        response = self.client.post(
            "/api/token/refresh/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("access_token", response.cookies)

    @patch("users.views.send_password_reset_email")
    def test_password_reset_has_generic_response(self, mocked_email):
        """Password reset should not reveal whether an account exists."""
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        existing_response = self.client.post(
            "/api/password_reset/",
            {"email": self.email},
            format="json",
        )

        missing_response = self.client.post(
            "/api/password_reset/",
            {"email": "unknown@example.com"},
            format="json",
        )

        self.assertEqual(existing_response.status_code, 200)
        self.assertEqual(missing_response.status_code, 200)
        self.assertEqual(
            existing_response.data["detail"],
            missing_response.data["detail"],
        )
        mocked_email.assert_called_once_with(user)

    def test_password_confirm_changes_password(self):
        """A valid reset token should allow a new password."""
        user = User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        new_password = "NewPassword123!"

        response = self.client.post(
            f"/api/password_confirm/{uid}/{token}/",
            {
                "new_password": new_password,
                "confirm_password": new_password,
            },
            format="json",
        )

        self.assertEqual(response.status_code, 200)

        user.refresh_from_db()
        self.assertTrue(user.check_password(new_password))

    def test_logout_removes_authentication_cookies(self):
        """Logout should remove access and refresh cookies."""
        User.objects.create_user(
            email=self.email,
            password=self.password,
            is_active=True,
        )

        self.client.post(
            "/api/login/",
            {
                "email": self.email,
                "password": self.password,
            },
            format="json",
        )

        response = self.client.post(
            "/api/logout/",
            {},
            format="json",
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.cookies["access_token"]["max-age"],
            0,
        )
        self.assertEqual(
            response.cookies["refresh_token"]["max-age"],
            0,
        )