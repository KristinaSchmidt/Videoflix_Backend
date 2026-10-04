from django.contrib import admin

from .models import Video


@admin.register(Video)
class VideoAdmin(admin.ModelAdmin):
    """Configure video management in the Django admin."""

    list_display = (
        "title",
        "category",
        "created_at",
    )
    list_filter = ("category",)
    search_fields = ("title",)