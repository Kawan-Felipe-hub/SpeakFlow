from __future__ import annotations

from datetime import datetime
from typing import Any, Literal, Optional
from uuid import UUID

from ninja import Schema


class ErrorOut(Schema):
    detail: str


class RegisterIn(Schema):
    username: str
    email: str
    password: str


class LoginIn(Schema):
    username: str
    password: str


class TokenOut(Schema):
    access: str
    refresh: str


class VoiceSessionCreateIn(Schema):
    topic: str


class VoiceSessionOut(Schema):
    id: int
    user_id: int
    started_at: datetime
    ended_at: Optional[datetime]
    topic: str
    total_messages: int


class SessionMessageOut(Schema):
    id: int
    session_id: int
    role: Literal["user", "assistant"]
    text: str
    audio_url: str
    pronunciation_score: dict[str, Any]
    created_at: datetime


class SendMessageOut(Schema):
    user_message: SessionMessageOut
    assistant_message: SessionMessageOut


class PronunciationOut(Schema):
    overall_score: float | None
    accuracy_score: float | None = None
    fluency_score: float | None = None
    completeness_score: float | None = None
    word_scores: list[dict[str, object]] = []


class SessionMessageReplyOut(Schema):
    reply_text: str
    reply_audio_url: str
    corrections: list[str]
    new_flashcards: list[FlashCardOut]
    pronunciation: PronunciationOut


class FlashCardCreateIn(Schema):
    front: str
    back: str
    created_from_session_id: Optional[int] = None


class FlashCardOut(Schema):
    id: int
    user_id: int
    front: str
    back: str
    easiness_factor: float
    interval_days: int
    repetitions: int
    next_review_at: datetime
    created_from_session_id: Optional[int]


class ReviewIn(Schema):
    flashcard_id: int
    quality_score: int


class ReviewOut(Schema):
    flashcard: FlashCardOut
    reviewed_at: datetime
    quality_score: int
    new_interval: int


class DashboardStatsOut(Schema):
    streak: int
    total_sessions: int
    due_flashcards: int
    recent_sessions: list[VoiceSessionOut]

