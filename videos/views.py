"""Views for video metadata and HLS streaming."""

from pathlib import Path

from django.conf import settings
from django.http import FileResponse, Http404
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from .models import Video
from .serializers import VideoSerializer


ALLOWED_RESOLUTIONS = {
    "480p",
    "720p",
    "1080p",
}


class VideoListView(ListAPIView):
    """Return all available videos for authenticated users."""

    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return all videos ordered by creation date."""
        return Video.objects.all()


class HLSPlaylistView(APIView):
    """Serve an HLS playlist for an authenticated user."""

    permission_classes = [IsAuthenticated]

    def get(self, request, video_id, resolution):
        """Return the requested index.m3u8 playlist."""
        if resolution not in ALLOWED_RESOLUTIONS:
            raise Http404

        playlist_path = (
            Path(settings.MEDIA_ROOT)
            / "videos"
            / str(video_id)
            / resolution
            / "index.m3u8"
        )

        if not playlist_path.exists():
            raise Http404

        return FileResponse(
            open(playlist_path, "rb"),
            content_type="application/vnd.apple.mpegurl",
        )


class HLSSegmentView(APIView):
    """Serve an HLS transport stream segment."""

    permission_classes = [IsAuthenticated]

    def get(self, request, video_id, resolution, segment):
        """Return a requested HLS .ts segment."""
        if resolution not in ALLOWED_RESOLUTIONS:
            raise Http404

        if not segment.endswith(".ts"):
            raise Http404

        segment_name = Path(segment).name

        segment_path = (
            Path(settings.MEDIA_ROOT)
            / "videos"
            / str(video_id)
            / resolution
            / segment_name
        )

        if not segment_path.exists():
            raise Http404

        return FileResponse(
            open(segment_path, "rb"),
            content_type="video/mp2t",
        )