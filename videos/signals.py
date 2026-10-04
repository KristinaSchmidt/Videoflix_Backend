"""Signals used to start background video processing."""

import django_rq
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import Video
from .tasks import process_video


@receiver(post_save, sender=Video)
def start_video_processing(sender, instance, created, **kwargs):
    """Queue HLS conversion after a new video has been created."""
    if created and instance.video_file:
        queue = django_rq.get_queue("default")
        queue.enqueue(process_video, instance.id)