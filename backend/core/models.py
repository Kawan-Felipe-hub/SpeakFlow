from __future__ import annotations

from typing import Any

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone


class User(AbstractUser):
    level = models.CharField(max_length=16, default="basic")
    streak_days = models.PositiveIntegerField(default=0)
    total_sessions = models.PositiveIntegerField(default=0)


class VoiceSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="voice_sessions")
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(null=True, blank=True)
    topic = models.CharField(max_length=64)
    total_messages = models.PositiveIntegerField(default=0)

    class Meta:
        indexes = [
            models.Index(fields=["user", "started_at"]),
            models.Index(fields=["topic"]),
        ]


class SessionMessage(models.Model):
    class Role(models.TextChoices):
        USER = "user", "User"
        ASSISTANT = "assistant", "Assistant"

    session = models.ForeignKey(VoiceSession, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=16, choices=Role.choices)
    text = models.TextField()
    audio_url = models.URLField(blank=True, default="")
    pronunciation_score = models.JSONField(default=dict, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        indexes = [
            models.Index(fields=["session", "created_at"]),
            models.Index(fields=["role"]),
        ]


class FlashCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="flashcards")
    front = models.TextField()
    back = models.TextField()

    easiness_factor = models.FloatField(default=2.5)
    interval_days = models.PositiveIntegerField(default=1)
    repetitions = models.PositiveIntegerField(default=0)
    next_review_at = models.DateTimeField(default=timezone.now)

    created_from_session = models.ForeignKey(
        VoiceSession,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_flashcards",
    )

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=["user", "next_review_at"]),
        ]


class ReviewLog(models.Model):
    flashcard = models.ForeignKey(FlashCard, on_delete=models.CASCADE, related_name="review_logs")
    reviewed_at = models.DateTimeField(default=timezone.now)
    quality_score = models.PositiveSmallIntegerField()
    new_interval = models.PositiveIntegerField()

    class Meta:
        indexes = [
            models.Index(fields=["flashcard", "reviewed_at"]),
        ]


def sm2_review(
    *,
    easiness_factor: float,
    interval_days: int,
    repetitions: int,
    quality_score: int,
) -> dict[str, Any]:
    if quality_score < 0 or quality_score > 5:
        raise ValueError("quality_score must be between 0 and 5")

    ef = easiness_factor
    rep = repetitions
    interval = interval_days

    if quality_score < 3:
        rep = 0
        interval = 1
    else:
        if rep == 0:
            interval = 1
        elif rep == 1:
            interval = 6
        else:
            interval = int(round(interval * ef))
        rep += 1

    ef = ef + (0.1 - (5 - quality_score) * (0.08 + (5 - quality_score) * 0.02))
    if ef < 1.3:
        ef = 1.3

    return {
        "easiness_factor": float(ef),
        "interval_days": int(interval),
        "repetitions": int(rep),
    }

