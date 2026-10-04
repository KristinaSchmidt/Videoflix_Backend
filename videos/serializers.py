from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata for the Videoflix API."""

    class Meta:
        """Configure fields exposed by the video endpoint."""

        model = Video
        fields = (
            "id",
            "title",
            "description",
            "created_at",
            "video_file",
            "thumbnail",
            "category",
        )
        read_only_fields = ("id", "created_at")