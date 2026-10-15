
from django.db import models


class Video(models.Model):
    """Store metadata and processing state for a Videoflix video."""

    CATEGORY_CHOICES = [
        ("documentary", "Documentary"),
        ("drama", "Drama"),
        ("romance", "Romance"),
    ]

    PROCESSING_STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("completed", "Completed"),
        ("failed", "Failed"),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    video_file = models.FileField(upload_to="videos/")
    thumbnail = models.ImageField(
        upload_to="thumbnails/",
        blank=True,
        null=True,
    )
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
    )
    processing_status = models.CharField(
        max_length=20,
        choices=PROCESSING_STATUS_CHOICES,
        default="pending",
        db_index=True,
    )

    class Meta:
        """Define the default ordering for video queries."""

        ordering = ["-created_at"]

    def __str__(self):
        """Return the video title."""
        return self.title
