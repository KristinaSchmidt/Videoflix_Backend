
"""Background tasks for Videoflix video processing."""

import logging

from .models import Video
from .utils import convert_video_to_hls


logger = logging.getLogger(__name__)


def process_video(video_id):
    """Convert a video and track its processing status."""
    video = Video.objects.get(pk=video_id)

    video.processing_status = "processing"
    video.save(update_fields=["processing_status"])

    try:
        convert_video_to_hls(video)
    except Exception:
        video.processing_status = "failed"
        video.save(update_fields=["processing_status"])

        logger.exception(
            "Video processing failed: video=%s",
            video_id,
        )
        raise

    video.processing_status = "completed"
    video.save(update_fields=["processing_status"])

    logger.info(
        "Video processing completed: video=%s",
        video_id,
    )
