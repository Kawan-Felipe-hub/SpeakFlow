from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from pathlib import Path
import os
from typing import Any, Optional

from django.conf import settings
from django.contrib.auth import authenticate
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.http import HttpRequest
from ninja import NinjaAPI, Router
from ninja.files import UploadedFile
from rest_framework_simplejwt.tokens import RefreshToken

from core.auth import SimpleJWTAuth
from core.integrations.azure_speech import recognize_and_assess, synthesize_tts
from core.integrations.groq_llm import tutor_reply
from core.models import FlashCard, ReviewLog, SessionMessage, User, VoiceSession, sm2_review
from core.schemas import (
    ErrorOut,
    FlashCardCreateIn,
    FlashCardOut,
    LoginIn,
    RegisterIn,
    ReviewIn,
    ReviewOut,
    SessionMessageReplyOut,
    SessionMessageOut,
    TokenOut,
    VoiceSessionCreateIn,
    VoiceSessionOut,
)


api = NinjaAPI(title="SpeakFlow API", version="1.0", urls_namespace="api", auth=SimpleJWTAuth())
router = Router()


def issue_tokens(user: User) -> TokenOut:
    refresh = RefreshToken.for_user(user)
    return TokenOut(access=str(refresh.access_token), refresh=str(refresh))


@router.post("/auth/register/", response={201: TokenOut, 400: ErrorOut}, auth=None)
def register(request: HttpRequest, payload: RegisterIn) -> tuple[int, TokenOut] | tuple[int, ErrorOut]:
    if User.objects.filter(username=payload.username).exists():
        return 400, ErrorOut(detail="Username already exists.")
    if User.objects.filter(email=payload.email).exists():
        return 400, ErrorOut(detail="Email already exists.")

    user = User(username=payload.username, email=payload.email)
    user.set_password(payload.password)
    user.save()
    return 201, issue_tokens(user)


@router.post("/auth/login/", response={200: TokenOut, 401: ErrorOut}, auth=None)
def login(request: HttpRequest, payload: LoginIn) -> tuple[int, TokenOut] | tuple[int, ErrorOut]:
    user = authenticate(request, username=payload.username, password=payload.password)
    if user is None:
        return 401, ErrorOut(detail="Invalid credentials.")
    return 200, issue_tokens(user)  # type: ignore[arg-type]


def require_user(request: HttpRequest) -> User:
    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        raise PermissionError("Authentication required")
    return user  # type: ignore[return-value]


@router.get("/sessions/", response=list[VoiceSessionOut])
def list_sessions(request: HttpRequest) -> list[VoiceSessionOut]:
    user = require_user(request)
    qs = VoiceSession.objects.filter(user=user).order_by("-started_at")
    return [
        VoiceSessionOut(
            id=s.id,
            user_id=s.user_id,
            started_at=s.started_at,
            ended_at=s.ended_at,
            topic=s.topic,
            total_messages=s.total_messages,
        )
        for s in qs
    ]


@router.get("/sessions/{session_id}/", response={200: VoiceSessionOut, 404: ErrorOut})
def get_session(request: HttpRequest, session_id: int) -> tuple[int, VoiceSessionOut] | tuple[int, ErrorOut]:
    user = require_user(request)
    session = VoiceSession.objects.filter(id=session_id, user=user).first()
    if session is None:
        return 404, ErrorOut(detail="Session not found.")
    return 200, VoiceSessionOut(
        id=session.id,
        user_id=session.user_id,
        started_at=session.started_at,
        ended_at=session.ended_at,
        topic=session.topic,
        total_messages=session.total_messages,
    )


@router.get("/sessions/{session_id}/messages/", response={200: list[SessionMessageOut], 404: ErrorOut})
def get_session_messages(request: HttpRequest, session_id: int) -> tuple[int, list[SessionMessageOut]] | tuple[int, ErrorOut]:
    user = require_user(request)
    session = VoiceSession.objects.filter(id=session_id, user=user).first()
    if session is None:
        return 404, ErrorOut(detail="Session not found.")
    
    messages = SessionMessage.objects.filter(session=session).order_by("created_at")
    return 200, [
        SessionMessageOut(
            id=m.id,
            session_id=m.session_id,
            role=m.role,
            text=m.text,
            audio_url=m.audio_url,
            pronunciation_score=m.pronunciation_score,
            created_at=m.created_at,
        )
        for m in messages
    ]


@router.post("/sessions/", response={201: VoiceSessionOut})
def create_session(request: HttpRequest, payload: VoiceSessionCreateIn) -> tuple[int, VoiceSessionOut]:
    user = require_user(request)
    s = VoiceSession.objects.create(user=user, topic=payload.topic)
    user.total_sessions = VoiceSession.objects.filter(user=user).count()
    user.save(update_fields=["total_sessions"])
    return 201, VoiceSessionOut(
        id=s.id,
        user_id=s.user_id,
        started_at=s.started_at,
        ended_at=s.ended_at,
        topic=s.topic,
        total_messages=s.total_messages,
    )


@router.delete("/sessions/{session_id}/", response={204: None, 404: ErrorOut})
def delete_session(request: HttpRequest, session_id: int) -> tuple[int, None] | tuple[int, ErrorOut]:
    user = require_user(request)
    session = VoiceSession.objects.filter(id=session_id, user=user).first()
    if session is None:
        return 404, ErrorOut(detail="Session not found.")
    session.delete()
    user.total_sessions = VoiceSession.objects.filter(user=user).count()
    user.save(update_fields=["total_sessions"])
    return 204, None


def _save_audio(file: UploadedFile) -> str:
    # Store in MEDIA_ROOT using default storage. Return absolute URL-ish path.
    now = datetime.now(timezone.utc).strftime("%Y%m%d/%H%M%S")
    rel_path = f"uploads/audio/{now}_{file.name}"
    saved_path = default_storage.save(rel_path, file)
    return settings.MEDIA_URL + saved_path


@router.post(
    "/sessions/{session_id}/message/",
    response={200: SessionMessageReplyOut, 404: ErrorOut, 400: ErrorOut},
)
async def post_message(
    request: HttpRequest,
    session_id: int,
    audio: UploadedFile = None,
    text: Optional[str] = None,
) -> tuple[int, SessionMessageReplyOut] | tuple[int, ErrorOut]:
    """
    Fluxo central (async):
    - STT + Pronunciation (Azure)
    - LLM tutor (Groq)
    - TTS (Azure)
    - Persistência de mensagens + criação automática de flashcards sugeridos
    """
    try:
        print(f"\n{'='*50}")
        print(f"=== INICIANDO POST MESSAGE ===")
        print(f"Session ID: {session_id}")
        print(f"Audio: {audio}")
        print(f"Audio name: {audio.name if audio else 'None'}")
        print(f"Audio size: {audio.size if audio else 'None'}")
        print(f"Audio type: {audio.content_type if audio else 'None'}")
        print(f"Text: {text}")
        print(f"Request FILES: {request.FILES}")
        print(f"Request POST: {request.POST}")
        print(f"{'='*50}\n")
        
        if audio is None:
            print("ERRO: Arquivo de áudio não enviado")
            return 400, ErrorOut(detail="Arquivo de áudio é obrigatório.")
        
        user = require_user(request)
        print(f"User authenticated: {user.username}")

        from asgiref.sync import sync_to_async

        session = await sync_to_async(
            lambda: VoiceSession.objects.filter(id=session_id, user=user).first()
        )()
        if session is None:
            return 404, ErrorOut(detail="Session not found.")

        # 1) Read audio bytes once (for Azure) and save file
        print("PASSO 1: Lendo áudio...")
        try:
            wav_bytes = await sync_to_async(audio.read)()
            print(f"Áudio lido com sucesso: {len(wav_bytes)} bytes")
        except Exception as e:
            print(f"ERRO AO LER ÁUDIO: {e}")
            import traceback
            traceback.print_exc()
            return 400, ErrorOut(detail="Falha ao ler arquivo de áudio.")

        try:
            # Create a new file-like object from bytes for saving
            from django.core.files.uploadedfile import SimpleUploadedFile
            audio_for_save = SimpleUploadedFile(audio.name, wav_bytes, audio.content_type)
            audio_url = await asyncio.to_thread(_save_audio, audio_for_save)
        except Exception:
            audio_url = ""

        # 2) Azure STT + Pronunciation
        print("PASSO 2: Iniciando STT + Pronunciation...")
        
        # Log das variáveis de ambiente para debug
        azure_key = os.environ.get("AZURE_SPEECH_KEY", "")
        azure_region = os.environ.get("AZURE_SPEECH_REGION", "")
        azure_language = os.environ.get("AZURE_SPEECH_LANGUAGE", "en-US")
        
        print(f"AZURE_SPEECH_KEY (primeiros 10 chars): {azure_key[:10] if azure_key else 'NOT SET'}")
        print(f"AZURE_SPEECH_REGION: {azure_region}")
        print(f"AZURE_SPEECH_LANGUAGE: {azure_language}")
        
        if not azure_key or not azure_region:
            print("ERRO: Variáveis de ambiente Azure não configuradas")
            return 400, ErrorOut(detail="Configuração Azure Speech não encontrada.")
        
        try:
            stt_res = await recognize_and_assess(
                wav_bytes=wav_bytes,
                key=azure_key,
                region=azure_region,
                language=azure_language,
                timeout_s=float(os.environ.get("AZURE_STT_TIMEOUT_S", "20")),
                content_type=audio.content_type,
            )
            transcript = stt_res.transcript.strip()
            print(f"STT concluído. Transcript: '{transcript}'")
            print(f"Pronunciation scores - Overall: {stt_res.overall_score}, Accuracy: {stt_res.accuracy_score}")
        except Exception as e:
            print(f"ERRO NO STT: {e}")
            import traceback
            traceback.print_exc()
            return 400, ErrorOut(detail="Falha no STT/Pronunciation (Azure indisponível ou timeout).")

        # 3) Build session history (last 10 messages)
        def _load_history() -> list[dict[str, str]]:
            qs = (
                SessionMessage.objects.filter(session=session)
                .order_by("-created_at")
                .values("role", "text")[:10]
            )
            history = []
            for item in reversed(list(qs)):
                role = "assistant" if item["role"] == SessionMessage.Role.ASSISTANT else "user"
                history.append({"role": role, "content": str(item["text"])})
            return history

        history = await sync_to_async(_load_history)()

        # System prompt from file
        try:
            system_prompt = (Path(settings.BASE_DIR) / "prompts" / "tutor_system.txt").read_text(encoding="utf-8")
        except Exception:
            return 400, ErrorOut(detail="Prompt do tutor não encontrado (prompts/tutor_system.txt).")

        # 3) Groq LLM
        print("PASSO 3: Iniciando LLM (Groq)...")
        try:
            llm = await tutor_reply(
                api_key=os.environ.get("GROQ_API_KEY", ""),
                model=os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile"),
                system_prompt=system_prompt,
                history=history,
                transcript=transcript,
            )
            reply_text = llm.reply_text or "Could you say that again in a different way?"
            print(f"LLM concluído. Reply: '{reply_text}'")
            print(f"Corrections: {llm.corrections}")
            print(f"Vocab suggestions: {len(llm.vocab_suggestions)}")
        except Exception as e:
            print(f"ERRO NO LLM: {e}")
            import traceback
            traceback.print_exc()
            return 400, ErrorOut(detail="Falha ao gerar resposta (Groq indisponível ou timeout).")

        # 4) Azure TTS (generate bytes and save)
        print("PASSO 4: Iniciando TTS...")
        reply_audio_url = ""
        try:
            tts_bytes = await synthesize_tts(
                text=reply_text,
                key=os.environ.get("AZURE_SPEECH_KEY", ""),
                region=os.environ.get("AZURE_SPEECH_REGION", ""),
                voice=os.environ.get("AZURE_SPEECH_VOICE", "en-US-JennyNeural"),
                timeout_s=float(os.environ.get("AZURE_TTS_TIMEOUT_S", "20")),
            )
            print(f"TTS concluído. Áudio gerado: {len(tts_bytes)} bytes")

            def _save_tts_bytes() -> str:
                from datetime import datetime, timezone
                now = datetime.now(timezone.utc).strftime("%Y%m%d/%H%M%S")
                rel_path = f"uploads/tts/{now}_reply.wav"
                audio_file = ContentFile(tts_bytes)
                saved_path = default_storage.save(rel_path, audio_file)
                # Build absolute URL for frontend to access
                # Get the base URL from request or use default
                from urllib.parse import urljoin
                base_url = f"http://{request.get_host()}"
                url = urljoin(base_url, settings.MEDIA_URL + saved_path.lstrip('/'))
                print(f"Saved path: {saved_path}, Full URL: {url}")
                return url

            reply_audio_url = await asyncio.to_thread(_save_tts_bytes)
            print(f"TTS salvo em: {reply_audio_url}")
        except Exception as e:
            print(f"ERRO NO TTS: {e}")
            import traceback
            traceback.print_exc()
            reply_audio_url = ""

        pronunciation_payload: dict[str, Any] = {
            "provider": "azure",
            "overall_score": stt_res.overall_score,
            "accuracy_score": stt_res.accuracy_score,
            "fluency_score": stt_res.fluency_score,
            "completeness_score": stt_res.completeness_score,
            "word_scores": [
                {"word": w.word, "accuracy_score": w.accuracy_score, "error_type": w.error_type}
                for w in stt_res.word_scores
            ],
            "raw": stt_res.raw,
        }

        # 5) Save messages + 6) Create flashcards suggested
        print("PASSO 5: Persistindo mensagens e flashcards...")
        def _persist_and_create() -> tuple[SessionMessage, SessionMessage, list[FlashCard]]:
            with transaction.atomic():
                user_msg = SessionMessage.objects.create(
                    session=session,
                    role=SessionMessage.Role.USER,
                    text=(text or "").strip() or transcript,
                    audio_url=audio_url,
                    pronunciation_score=pronunciation_payload,
                )
                assistant_msg = SessionMessage.objects.create(
                    session=session,
                    role=SessionMessage.Role.ASSISTANT,
                    text=reply_text,
                    audio_url=reply_audio_url,
                    pronunciation_score={},
                )

                new_cards: list[FlashCard] = []
                for item in llm.vocab_suggestions[:3]:
                    new_cards.append(
                        FlashCard.objects.create(
                            user=user,
                            front=item["front"],
                            back=item["back"],
                            created_from_session=session,
                        )
                    )

                session.total_messages = SessionMessage.objects.filter(session=session).count()
                session.save(update_fields=["total_messages"])
            return user_msg, assistant_msg, new_cards

        try:
            user_msg, assistant_msg, new_cards = await sync_to_async(_persist_and_create)()
            print(f"Persistência concluída. {len(new_cards)} flashcards criados.")
        except Exception as e:
            print(f"ERRO NA PERSISTÊNCIA: {e}")
            import traceback
            traceback.print_exc()
            return 400, ErrorOut(detail="Falha ao persistir mensagens/flashcards.")

        new_flashcards_out = [
            FlashCardOut(
                id=c.id,
                user_id=c.user_id,
                front=c.front,
                back=c.back,
                easiness_factor=c.easiness_factor,
                interval_days=c.interval_days,
                repetitions=c.repetitions,
                next_review_at=c.next_review_at,
                created_from_session_id=c.created_from_session_id,
            )
            for c in new_cards
        ]

        print("PASSO 6: Preparando resposta final...")
        response = SessionMessageReplyOut(
            reply_text=reply_text,
            reply_audio_url=reply_audio_url,
            corrections=llm.corrections,
            new_flashcards=new_flashcards_out,
            pronunciation={
                "overall_score": stt_res.overall_score,
                "accuracy_score": stt_res.accuracy_score,
                "fluency_score": stt_res.fluency_score,
                "completeness_score": stt_res.completeness_score,
                "word_scores": pronunciation_payload["word_scores"],
            },
        )
        print(f"Resposta preparada. reply_text: '{reply_text}', reply_audio_url: '{reply_audio_url}'")
        print(f"{'='*50}\n")
        return 200, response
        
    except Exception as e:
        # Log completo do erro
        import traceback
        from datetime import datetime
        
        error_msg = f"""
=== ERRO 500 DETECTADO ===
Timestamp: {datetime.now().isoformat()}
Error: {str(e)}
Traceback:
{traceback.format_exc()}
"""
        
        # Salvar em arquivo
        with open("error_log.txt", "a", encoding="utf-8") as f:
            f.write(error_msg)
        
        # Tentar imprimir no console também
        print(error_msg)
        
        return 500, ErrorOut(detail="An error occurred processing your message. Please try again.")


@router.get("/flashcards/", response=list[FlashCardOut])
def list_flashcards(request: HttpRequest) -> list[FlashCardOut]:
    user = require_user(request)
    qs = FlashCard.objects.filter(user=user).order_by("-id")
    return [
        FlashCardOut(
            id=c.id,
            user_id=c.user_id,
            front=c.front,
            back=c.back,
            easiness_factor=c.easiness_factor,
            interval_days=c.interval_days,
            repetitions=c.repetitions,
            next_review_at=c.next_review_at,
            created_from_session_id=c.created_from_session_id,
        )
        for c in qs
    ]


@router.post("/flashcards/", response={201: FlashCardOut, 400: ErrorOut})
def create_flashcard(
    request: HttpRequest, payload: FlashCardCreateIn
) -> tuple[int, FlashCardOut] | tuple[int, ErrorOut]:
    user = require_user(request)
    created_from_session = None
    if payload.created_from_session_id is not None:
        created_from_session = VoiceSession.objects.filter(
            id=payload.created_from_session_id, user=user
        ).first()
        if created_from_session is None:
            return 400, ErrorOut(detail="created_from_session_id inválido.")

    c = FlashCard.objects.create(
        user=user,
        front=payload.front,
        back=payload.back,
        created_from_session=created_from_session,
    )
    return 201, FlashCardOut(
        id=c.id,
        user_id=c.user_id,
        front=c.front,
        back=c.back,
        easiness_factor=c.easiness_factor,
        interval_days=c.interval_days,
        repetitions=c.repetitions,
        next_review_at=c.next_review_at,
        created_from_session_id=c.created_from_session_id,
    )


@router.get("/flashcards/due/", response=list[FlashCardOut])
def due_flashcards(request: HttpRequest) -> list[FlashCardOut]:
    user = require_user(request)
    now = datetime.now(timezone.utc)
    qs = FlashCard.objects.filter(user=user, next_review_at__lte=now).order_by("next_review_at")
    return [
        FlashCardOut(
            id=c.id,
            user_id=c.user_id,
            front=c.front,
            back=c.back,
            easiness_factor=c.easiness_factor,
            interval_days=c.interval_days,
            repetitions=c.repetitions,
            next_review_at=c.next_review_at,
            created_from_session_id=c.created_from_session_id,
        )
        for c in qs
    ]


@router.post("/flashcards/review/", response={200: ReviewOut, 400: ErrorOut, 404: ErrorOut})
def review_flashcard(
    request: HttpRequest, payload: ReviewIn
) -> tuple[int, ReviewOut] | tuple[int, ErrorOut]:
    user = require_user(request)
    card = FlashCard.objects.filter(id=payload.flashcard_id, user=user).first()
    if card is None:
        return 404, ErrorOut(detail="Flashcard não encontrado.")

    try:
        result = sm2_review(
            easiness_factor=card.easiness_factor,
            interval_days=card.interval_days,
            repetitions=card.repetitions,
            quality_score=payload.quality_score,
        )
    except ValueError as e:
        return 400, ErrorOut(detail=str(e))

    now = datetime.now(timezone.utc)
    new_interval = int(result["interval_days"])
    card.easiness_factor = float(result["easiness_factor"])
    card.interval_days = new_interval
    card.repetitions = int(result["repetitions"])
    card.next_review_at = now.replace(microsecond=0) + timedelta(days=new_interval)
    card.save(
        update_fields=[
            "easiness_factor",
            "interval_days",
            "repetitions",
            "next_review_at",
            "updated_at",
        ]
    )

    log = ReviewLog.objects.create(
        flashcard=card,
        reviewed_at=now,
        quality_score=payload.quality_score,
        new_interval=new_interval,
    )

    return 200, ReviewOut(
        flashcard=FlashCardOut(
            id=card.id,
            user_id=card.user_id,
            front=card.front,
            back=card.back,
            easiness_factor=card.easiness_factor,
            interval_days=card.interval_days,
            repetitions=card.repetitions,
            next_review_at=card.next_review_at,
            created_from_session_id=card.created_from_session_id,
        ),
        reviewed_at=log.reviewed_at,
        quality_score=log.quality_score,
        new_interval=log.new_interval,
    )


api.add_router("", router)

