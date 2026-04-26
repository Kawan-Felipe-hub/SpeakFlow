from __future__ import annotations

from django.contrib import admin

from core.models import FlashCard, ReviewLog, SessionMessage, User, VoiceSession


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("id", "username", "email", "level", "streak_days", "total_sessions", "is_active")
    search_fields = ("username", "email")


@admin.register(VoiceSession)
class VoiceSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "topic", "started_at", "ended_at", "total_messages")
    list_filter = ("topic",)
    search_fields = ("user__username", "user__email")


@admin.register(SessionMessage)
class SessionMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "session", "role", "created_at")
    list_filter = ("role",)
    search_fields = ("session__id",)


@admin.register(FlashCard)
class FlashCardAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "next_review_at", "repetitions", "interval_days", "easiness_factor")
    search_fields = ("user__username", "user__email", "front", "back")


@admin.register(ReviewLog)
class ReviewLogAdmin(admin.ModelAdmin):
    list_display = ("id", "flashcard", "reviewed_at", "quality_score", "new_interval")

