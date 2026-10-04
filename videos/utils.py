"""Utility functions for Videoflix video processing."""

import subprocess
from pathlib import Path

from django.conf import settings


RESOLUTIONS = {
    "480p": "854:480",
    "720p": "1280:720",
    "1080p": "1920:1080",
}


def convert_video_to_hls(video):
    """Convert an uploaded video into HLS streams using FFmpeg."""
    input_path = Path(video.video_file.path)

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

        command = [
            "ffmpeg",
            "-y",
            "-i",
            str(input_path),
            "-vf",
            f"scale={size}:force_original_aspect_ratio=decrease",
            "-c:v",
            "libx264",
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

        subprocess.run(
            command,
            check=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )