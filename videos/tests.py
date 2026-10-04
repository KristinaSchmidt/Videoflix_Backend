"""Tests for the Videoflix video API and HLS streaming."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

from .models import Video


class VideoAPITests(APITestCase):
    """Test authenticated video metadata access."""

    def setUp(self):
        """Create an authenticated user for video API tests."""
        self.user = User.objects.create_user(
            email="video@example.com",
            password="TestPassword123!",
            is_active=True,
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.cookies["access_token"] = str(
            refresh.access_token
        )

    @patch("videos.signals.django_rq.get_queue")
    def test_video_list_returns_frontend_fields(self, mocked_queue):
        """Video endpoint should return fields expected by frontend."""
        mocked_queue.return_value.enqueue.return_value = None

        thumbnail = SimpleUploadedFile(
            "thumbnail.jpg",
            b"thumbnail-content",
            content_type="image/jpeg",
        )

        video_file = SimpleUploadedFile(
            "video.mp4",
            b"video-content",
            content_type="video/mp4",
        )

        Video.objects.create(
            title="Test Video",
            description="Test description",
            category="drama",
            thumbnail=thumbnail,
            video_file=video_file,
        )

        response = self.client.get("/api/video/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)

        video_data = response.data[0]

        self.assertEqual(video_data["title"], "Test Video")
        self.assertEqual(
            video_data["description"],
            "Test description",
        )
        self.assertEqual(video_data["category"], "drama")
        self.assertIn("thumbnail_url", video_data)

    def test_video_list_requires_authentication(self):
        """Anonymous users should not access video metadata."""
        self.client.cookies.clear()

        response = self.client.get("/api/video/")

        self.assertEqual(response.status_code, 401)


class HLSStreamingTests(APITestCase):
    """Test authenticated HLS playlist and segment delivery."""

    def setUp(self):
        """Create an authenticated user for streaming tests."""
        self.user = User.objects.create_user(
            email="stream@example.com",
            password="TestPassword123!",
            is_active=True,
        )

        refresh = RefreshToken.for_user(self.user)

        self.client.cookies["access_token"] = str(
            refresh.access_token
        )

        self.temp_directory = tempfile.TemporaryDirectory()
        self.media_root = Path(self.temp_directory.name)

        self.settings_override = override_settings(
            MEDIA_ROOT=self.media_root
        )
        self.settings_override.enable()

    def tearDown(self):
        """Remove temporary HLS files after every test."""
        self.settings_override.disable()
        self.temp_directory.cleanup()

    def create_hls_files(self, video_id=1, resolution="480p"):
        """Create a small playlist and segment for streaming tests."""
        directory = (
            self.media_root
            / "videos"
            / str(video_id)
            / resolution
        )
        directory.mkdir(parents=True, exist_ok=True)

        playlist = directory / "index.m3u8"
        playlist.write_text(
            "#EXTM3U\n#EXTINF:10,\nsegment_000.ts\n",
            encoding="utf-8",
        )

        segment = directory / "segment_000.ts"
        segment.write_bytes(b"test-segment")

    def test_hls_playlist_is_available(self):
        """Authenticated users should receive an HLS playlist."""
        self.create_hls_files()

        response = self.client.get(
            "/api/video/1/480p/index.m3u8"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "application/vnd.apple.mpegurl",
        )

    def test_hls_segment_is_available(self):
        """Authenticated users should receive HLS segments."""
        self.create_hls_files()

        response = self.client.get(
            "/api/video/1/480p/segment_000.ts"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response["Content-Type"],
            "video/mp2t",
        )

    def test_invalid_resolution_returns_not_found(self):
        """Unsupported HLS resolutions should return HTTP 404."""
        response = self.client.get(
            "/api/video/1/360p/index.m3u8"
        )

        self.assertEqual(response.status_code, 404)

    def test_hls_requires_authentication(self):
        """Anonymous users should not access HLS streams."""
        self.create_hls_files()
        self.client.cookies.clear()

        response = self.client.get(
            "/api/video/1/480p/index.m3u8"
        )

        self.assertEqual(response.status_code, 401)