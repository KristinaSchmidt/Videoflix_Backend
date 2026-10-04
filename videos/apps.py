"""Application configuration for the videos app."""

from django.apps import AppConfig


class VideosConfig(AppConfig):
    """Configure the Videoflix videos application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "videos"

    def ready(self):
        """Register video signal handlers when Django starts."""
        import videos.signals  # noqa: F401