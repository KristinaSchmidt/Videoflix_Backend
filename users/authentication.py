"""Custom authentication classes for the Videoflix API."""

from rest_framework_simplejwt.authentication import JWTAuthentication


class CookieJWTAuthentication(JWTAuthentication):
    """Authenticate users with a JWT stored in an HTTP-only cookie."""

    def authenticate(self, request):
        """Read and validate the access token from the request cookie."""
        access_token = request.COOKIES.get("access_token")

        if access_token is None:
            return None

        validated_token = self.get_validated_token(access_token)
        user = self.get_user(validated_token)

        return user, validated_token