
"""Tests for the Videoflix video API and HLS streaming."""

import tempfile
from pathlib import Path
from unittest.mock import patch

from redis.exceptions import ConnectionError as RedisConnectionError
from rq import Retry

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from users.models import User

from .models import Video
from .serializers import VideoSerializer
from .tasks import process_video


class VideoAPITests(APITestCase):
    """Test authenticated video metadata and thumbnail access."""

    def setUp(self):
        """Create an authenticated user and temporary media directory."""
        self.user = User.objects.create_user(
            email="video@example.com",
            password="TestPassword123!",
            is_active=True,
        )

        refresh = RefreshToken.for_user(self.user)
        self.client.cookies["access_token"] = str(refresh.access_token)

        self.temp_directory = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=Path(self.temp_directory.name)
        )
        self.settings_override.enable()

    def tearDown(self):
        """Clean up temporary uploaded files."""
        self.settings_override.disable()
        self.temp_directory.cleanup()

    def create_video(self, with_thumbnail=True):
        """Create a video without starting a real background worker."""
        video_file = SimpleUploadedFile(
            "video.mp4",
            b"video-content",
            content_type="video/mp4",
        )

        fields = {
            "title": "Test Video",
            "description": "Test description",
            "category": "drama",
            "video_file": video_file,
        }

        if with_thumbnail:
            fields["thumbnail"] = SimpleUploadedFile(
                "thumbnail.png",
                b"thumbnail-content",
                content_type="image/png",
            )

        with patch("videos.signals.django_rq.get_queue"):
            video = Video.objects.create(**fields)

        return video

    def test_video_list_returns_frontend_fields(self):
        """Video endpoint should return fields expected by frontend."""
        self.create_video()

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

    def test_missing_thumbnail_uses_default_image(self):
        """Videos without thumbnails should use the default image."""
        video = self.create_video(with_thumbnail=False)

        data = VideoSerializer(video).data

        self.assertIn(
            "default-thumbnail",
            data["thumbnail_url"],
        )

    def test_uploaded_thumbnail_has_api_url(self):
        """Uploaded thumbnails should use the protected API route."""
        video = self.create_video()

        data = VideoSerializer(video).data

        self.assertEqual(
            data["thumbnail_url"],
            f"/api/video/{video.id}/thumbnail/",
        )

    def test_uploaded_thumbnail_can_be_downloaded(self):
        """Authenticated users should receive uploaded thumbnails."""
        video = self.create_video()

        response = self.client.get(
            f"/api/video/{video.id}/thumbnail/"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            b"".join(response.streaming_content),
            b"thumbnail-content",
        )

    def test_thumbnail_requires_authentication(self):
        """Anonymous users should not download thumbnails."""
        video = self.create_video()
        self.client.cookies.clear()

        response = self.client.get(
            f"/api/video/{video.id}/thumbnail/"
        )

        self.assertEqual(response.status_code, 401)

    def test_missing_thumbnail_returns_not_found(self):
        """Thumbnail endpoint should return 404 if no image exists."""
        video = self.create_video(with_thumbnail=False)

        response = self.client.get(
            f"/api/video/{video.id}/thumbnail/"
        )

        self.assertEqual(response.status_code, 404)

    def test_video_processing_is_queued_after_commit(self):
        """Background processing must wait for the database commit."""
        with patch("videos.signals.django_rq.get_queue") as get_queue:
            with self.captureOnCommitCallbacks(execute=True) as callbacks:
                video = Video.objects.create(
                    title="First Upload",
                    description="Test initial upload",
                    category="drama",
                    video_file=SimpleUploadedFile(
                        "first.mp4",
                        b"video-content",
                        content_type="video/mp4",
                    ),
                )

                get_queue.assert_not_called()

            self.assertEqual(len(callbacks), 1)
            get_queue.assert_called_once_with("default")
            get_queue.return_value.enqueue.assert_called_once()

            args = get_queue.return_value.enqueue.call_args.args

            self.assertEqual(args[1], video.id)


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




class VideoAdminUploadTests(APITestCase):
    """Test the first video upload through Django Admin."""

    def setUp(self):
        """Prepare an admin user and temporary media storage."""
        self.user = User.objects.create_superuser(
            email="admin-upload@example.com",
            password="TestPassword123!",
        )
        self.client.force_login(self.user)

        self.temp_directory = tempfile.TemporaryDirectory()
        self.settings_override = override_settings(
            MEDIA_ROOT=Path(self.temp_directory.name)
        )
        self.settings_override.enable()

    def tearDown(self):
        """Remove temporary uploaded files."""
        self.settings_override.disable()
        self.temp_directory.cleanup()

    def test_first_admin_upload_without_thumbnail(self):
        """First admin upload succeeds and queues processing after commit."""
        self.assertEqual(Video.objects.count(), 0)

        with patch("videos.signals.django_rq.get_queue") as get_queue:
            with self.captureOnCommitCallbacks(execute=True):
                response = self.client.post(
                    "/admin/videos/video/add/",
                    {
                        "title": "First Admin Upload",
                        "description": "Video without thumbnail",
                        "category": "drama",
                        "video_file": SimpleUploadedFile(
                            "first-upload.mp4",
                            b"test-video-content",
                            content_type="video/mp4",
                        ),
                        "_save": "Save",
                    },
                )

                get_queue.assert_not_called()

        self.assertEqual(response.status_code, 302)
        self.assertEqual(Video.objects.count(), 1)

        video = Video.objects.get()
        self.assertFalse(video.thumbnail)

        get_queue.assert_called_once_with("default")
        get_queue.return_value.enqueue.assert_called_once()
        args = get_queue.return_value.enqueue.call_args.args
        kwargs = get_queue.return_value.enqueue.call_args.kwargs
        self.assertEqual(args, (process_video, video.id))
        self.assertIsInstance(kwargs["retry"], Retry)
        self.assertEqual(kwargs["retry"].max, 3)

    def test_redis_failure_does_not_break_admin_upload(self):
        """The upload succeeds even when Redis cannot accept the job."""
        with patch("videos.signals.django_rq.get_queue") as get_queue:
            get_queue.side_effect = RedisConnectionError("Redis unavailable")
            with self.assertLogs("videos.signals", level="ERROR"):
                with self.captureOnCommitCallbacks(execute=True):
                    response = self.client.post(
                        "/admin/videos/video/add/",
                        {
                            "title": "Upload During Redis Outage",
                            "description": "Redis unavailable at commit",
                            "category": "drama",
                            "video_file": SimpleUploadedFile(
                                "redis-outage.mp4",
                                b"test-video-content",
                                content_type="video/mp4",
                            ),
                            "_save": "Save",
                        },
                    )
        self.assertEqual(response.status_code, 302)
        video = Video.objects.get(title="Upload During Redis Outage")
        self.assertEqual(video.processing_status, "pending")


class VideoProcessingStatusTests(APITestCase):
    """Check that worker processing results are saved to the database."""

    def setUp(self):
        with patch("videos.signals.django_rq.get_queue"):
            self.video = Video.objects.create(
                title="Processing status test",
                description="Test processing states",
                category="drama",
                video_file="videos/status-test.mp4",
            )

    @patch("videos.tasks.convert_video_to_hls")
    def test_successful_processing_marks_video_completed(self, convert):
        process_video(self.video.pk)
        self.video.refresh_from_db()
        self.assertEqual(self.video.processing_status, "completed")
        convert.assert_called_once()

    @patch("videos.tasks.convert_video_to_hls", side_effect=RuntimeError("FFmpeg failed"))
    def test_failed_processing_marks_video_failed(self, convert):
        with self.assertLogs("videos.tasks", level="ERROR"):
            with self.assertRaises(RuntimeError):
                process_video(self.video.pk)
        self.video.refresh_from_db()
        self.assertEqual(self.video.processing_status, "failed")
        convert.assert_called_once()
