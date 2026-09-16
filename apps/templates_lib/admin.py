"""
apps/templates_lib/admin.py — Admin for Resume Template catalog.
"""
from django.contrib import admin
from django.utils.html import format_html

from .models import ResumeTemplate


@admin.register(ResumeTemplate)
class ResumeTemplateAdmin(admin.ModelAdmin):
    list_display = [
        "name", "slug", "engine", "category",
        "supports_photo", "is_one_page_design", "ats_friendly", "is_active", "thumbnail_preview"
    ]
    list_filter = ["engine", "category", "is_active", "supports_photo", "ats_friendly"]
    search_fields = ["name", "slug"]
    readonly_fields = ["created_at", "thumbnail_preview"]
    prepopulated_fields = {"slug": ("name",)}

    def thumbnail_preview(self, obj):
        if obj.thumbnail:
            return format_html(
                '<img src="{}" style="height:80px;border-radius:4px;" />',
                obj.thumbnail.url
            )
        return "No thumbnail"
    thumbnail_preview.short_description = "Preview"
