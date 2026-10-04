from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated

from .models import Video
from .serializers import VideoSerializer


class VideoListView(ListAPIView):
    """Return all available videos for authenticated users."""

    serializer_class = VideoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Return videos ordered by their creation date."""
        return Video.objects.all()