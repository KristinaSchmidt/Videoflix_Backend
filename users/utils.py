from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import send_mail
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def send_activation_email(user):
    """Create an activation token and send the activation link by email."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_url = (
        f"{settings.FRONTEND_URL}/pages/auth/activate.html"
        f"?uid={uid}&token={token}"
    )

    send_mail(
        "Activate your Videoflix account",
        f"Activate your account: {activation_url}",
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
    )