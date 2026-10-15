
"""Signals used to start background video processing."""

import logging

import django_rq
from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from rq import Retry

from .models import Video
from .tasks import process_video


logger = logging.getLogger(__name__)


@receiver(post_save, sender=Video)
def start_video_processing(sender, instance, created, **kwargs):
    """Queue video processing after the database transaction commits."""
    if not created or not instance.video_file:
        return

    video_id = instance.id

    def enqueue_video():
        """Submit the video job to Redis."""
        try:
            queue = django_rq.get_queue("default")
            queue.enqueue(
                process_video,
                video_id,
                retry=Retry(
                    max=3,
                    interval=[30, 60, 120],
                ),
            )
        except Exception:
            logger.exception(
                "Could not enqueue video processing: video=%s",
                video_id,
            )
            raise

    transaction.on_commit(enqueue_video, robust=True)