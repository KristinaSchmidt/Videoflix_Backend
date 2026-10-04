"""Background tasks for Videoflix video processing."""

from .models import Video
from .utils import convert_video_to_hls


def process_video(video_id):
    """Load a video and create all required HLS resolutions."""
    video = Video.objects.get(pk=video_id)
    convert_video_to_hls(video)