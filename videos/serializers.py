
"""Serializers for Videoflix video data."""

from django.contrib.staticfiles.storage import staticfiles_storage
from django.urls import reverse
from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata required by the Videoflix frontend."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            "id",
            "title",
            "description",
            "created_at",
            "category",
            "thumbnail_url",
        )
        read_only_fields = fields

    def get_thumbnail_url(self, obj):
        """Return an uploaded thumbnail or the default image."""
        if obj.thumbnail:
            thumbnail_url = reverse(
                "video-thumbnail",
                kwargs={"video_id": obj.id},
            )
        else:
            thumbnail_url = staticfiles_storage.url(
                "videos/default-thumbnail.png"
            )

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(thumbnail_url)

        return thumbnail_url
