
"""Utility functions for Videoflix video processing."""

import logging
import subprocess
from pathlib import Path

from django.conf import settings


logger = logging.getLogger(__name__)

RESOLUTIONS = {
    "480p": "854:480",
    "720p": "1280:720",
    "1080p": "1920:1080",
}


def convert_video_to_hls(video):
    """Convert an uploaded video into HLS streams using FFmpeg."""
    input_path = Path(video.video_file.path)

    if not input_path.is_file():
        raise FileNotFoundError(
            f"Video source file not found: {input_path}"
        )

    for resolution, size in RESOLUTIONS.items():
        output_directory = (
            Path(settings.MEDIA_ROOT)
            / "videos"
            / str(video.id)
            / resolution
        )

        output_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        playlist_path = output_directory / "index.m3u8"
        segment_path = output_directory / "segment_%03d.ts"

        width, height = size.split(":")

        video_filter = (
            f"scale={width}:{height}:"
            "force_original_aspect_ratio=decrease:"
            "force_divisible_by=2,"
            "format=yuv420p"
        )

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            video_filter,
            "-c:v",
            "libx264",
            "-threads:v",
            "2",
            "-preset",
            "fast",
            "-crf",
            "23",
            "-c:a",
            "aac",
            "-b:a",
            "128k",
            "-hls_time",
            "10",
            "-hls_playlist_type",
            "vod",
            "-hls_segment_filename",
            str(segment_path),
            str(playlist_path),
        ]

        logger.info(
            "Starting HLS conversion: video=%s, resolution=%s",
            video.id,
            resolution,
        )

        try:
            subprocess.run(
                command,
                check=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                text=True,
            )
        except subprocess.CalledProcessError as error:
            logger.error(
                "FFmpeg conversion failed: video=%s, "
                "resolution=%s, exit_code=%s\n%s",
                video.id,
                resolution,
                error.returncode,
                error.stderr,
            )
            raise

        logger.info(
            "HLS conversion completed: video=%s, resolution=%s",
            video.id,
            resolution,
        )
