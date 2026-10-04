"""URL configuration for user registration and account activation."""

from django.urls import path

from .views import ActivateAccountView, RegisterView


urlpatterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path(
        "activate/<uidb64>/<token>/",
        ActivateAccountView.as_view(),
        name="activate",
    ),
]