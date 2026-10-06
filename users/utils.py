"""Email utilities for Videoflix account actions."""

from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode


def _send_html_email(subject, recipient, template_name, context, text_body):
    """Send an email with HTML and plain-text alternatives."""
    html_body = render_to_string(template_name, context)

    email = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[recipient],
    )
    email.attach_alternative(html_body, "text/html")
    email.send()


def send_activation_email(user):
    """Create an activation token and send the activation email."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    activation_url = (
        f"{settings.FRONTEND_URL}/pages/auth/activate.html"
        f"?uid={uid}&token={token}"
    )

    _send_html_email(
        subject="Confirm your email",
        recipient=user.email,
        template_name="emails/activation_email.html",
        context={
            "activation_url": activation_url,
            "user_email": user.email,
        },
        text_body=(
            "Thank you for registering with Videoflix.\n\n"
            "To complete your registration and verify your email address, "
            "please use the following link:\n"
            f"{activation_url}\n\n"
            "If you did not create an account with us, "
            "please disregard this email.\n\n"
            "Best regards,\n"
            "Your Videoflix Team."
        ),
    )


def send_password_reset_email(user):
    """Create a reset token and send the password reset email."""
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    token = default_token_generator.make_token(user)

    reset_url = (
        f"{settings.FRONTEND_URL}/pages/auth/confirm_password.html"
        f"?uid={uid}&token={token}"
    )

    _send_html_email(
        subject="Reset your Password",
        recipient=user.email,
        template_name="emails/password_reset_email.html",
        context={
            "reset_url": reset_url,
        },
        text_body=(
            "Hello,\n\n"
            "We recently received a request to reset your password. "
            "If you made this request, please use the following link:\n"
            f"{reset_url}\n\n"
            "If you did not request a password reset, "
            "please ignore this email.\n\n"
            "Best regards,\n"
            "Your Videoflix team!"
        ),
    )