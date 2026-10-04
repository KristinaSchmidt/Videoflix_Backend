"""URL configuration for video metadata and HLS streaming."""

from django.urls import path

from .views import (
    HLSPlaylistView,
    HLSSegmentView,
    VideoListView,
)


urlpatterns = [
    path(
        "",
        VideoListView.as_view(),
        name="video-list",
    ),
    path(
        "<int:video_id>/<str:resolution>/index.m3u8",
        HLSPlaylistView.as_view(),
        name="hls-playlist",
    ),
    path(
        "<int:video_id>/<str:resolution>/<str:segment>",
        HLSSegmentView.as_view(),
        name="hls-segment",
    ),
]