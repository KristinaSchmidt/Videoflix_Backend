"""Serializers for Videoflix video data."""

from rest_framework import serializers

from .models import Video


class VideoSerializer(serializers.ModelSerializer):
    """Serialize video metadata required by the Videoflix frontend."""

    thumbnail_url = serializers.SerializerMethodField()

    class Meta:
        """Configure the fields exposed by the video API."""

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
        """Return an absolute URL for the video thumbnail."""
        if not obj.thumbnail:
            return None

        request = self.context.get("request")

        if request:
            return request.build_absolute_uri(obj.thumbnail.url)

        return obj.thumbnail.url