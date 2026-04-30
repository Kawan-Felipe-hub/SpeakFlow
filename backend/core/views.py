from __future__ import annotations

import os
import json
import asyncio
from datetime import datetime
from typing import Dict, Any

from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.db import transaction
from django.conf import settings
from django.contrib.auth import authenticate
import logging

logger = logging.getLogger(__name__)

from core.models import User, VoiceSession, SessionMessage, FlashCard
from core.integrations.azure_speech import recognize_and_assess, synthesize_tts
from core.integrations.groq_client import groq_client
from rest_framework_simplejwt.tokens import RefreshToken

def issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def register_view(request: HttpRequest) -> JsonResponse:
    # Adicionar headers CORS manualmente
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        response["Access-Control-Max-Age"] = "86400"
        return response
    
    try:
        data = json.loads(request.body)
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        if not username or not email or not password:
            response = JsonResponse({"detail": "Username, email and password are required"}, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        if User.objects.filter(username=username).exists():
            response = JsonResponse({"detail": "Username already exists."}, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        if User.objects.filter(email=email).exists():
            response = JsonResponse({"detail": "Email already exists."}, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        
        tokens = issue_tokens(user)
        response = JsonResponse(tokens, status=201)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except json.JSONDecodeError as e:
        response = JsonResponse({"detail": f"Invalid JSON: {str(e)}"}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    except Exception as e:
        response = JsonResponse({"detail": str(e)}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
def login_view(request: HttpRequest) -> JsonResponse:
    # Adicionar headers CORS manualmente
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        response["Access-Control-Max-Age"] = "86400"
        return response
    
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            response = JsonResponse({"detail": "Username and password are required"}, status=400)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            response = JsonResponse({"detail": "Invalid credentials."}, status=401)
            response["Access-Control-Allow-Origin"] = "*"
            return response
            
        tokens = issue_tokens(user)
        response = JsonResponse(tokens, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        response = JsonResponse({"detail": str(e)}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@csrf_exempt
@require_http_methods(["GET", "POST", "OPTIONS"])
def sessions_view(request: HttpRequest) -> JsonResponse:
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
    
    try:
        if request.method == "GET":
            # For now, return empty sessions list - this can be expanded later
            sessions = []
            response = JsonResponse({"sessions": sessions}, status=200)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        elif request.method == "POST":
            # Create new session
            user = _get_user_from_request_sync(request)
            if not user:
                response = JsonResponse({"detail": "Authentication required"}, status=401)
                response["Access-Control-Allow-Origin"] = "*"
                return response
            
            # Create new voice session
            session = VoiceSession(
                user=user,
                topic="General Conversation",  # Default topic
                started_at=datetime.now()
            )
            session.save()
            
            response = JsonResponse({"id": session.id}, status=201)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
    except Exception as e:
        response = JsonResponse({"detail": str(e)}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def session_detail_view(request: HttpRequest, session_id: int) -> JsonResponse:
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
    
    try:
        user = _get_user_from_request_sync(request)
        if not user:
            response = JsonResponse({"detail": "Authentication required"}, status=401)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        # Get specific session
        try:
            session = VoiceSession.objects.get(id=session_id, user=user)
        except VoiceSession.DoesNotExist:
            response = JsonResponse({"detail": "Session not found"}, status=404)
            response["Access-Control-Allow-Origin"] = "*"
            return response
        
        # Return session data
        session_data = {
            "id": session.id,
            "topic": session.topic,
            "started_at": session.started_at.isoformat(),
            "ended_at": session.ended_at.isoformat() if session.ended_at else None,
            "total_messages": session.total_messages,
        }
        
        response = JsonResponse(session_data, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        response = JsonResponse({"detail": str(e)}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@csrf_exempt
@require_http_methods(["GET", "OPTIONS"])
def flashcards_due_view(request: HttpRequest) -> JsonResponse:
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
    
    try:
        # For now, return empty flashcards list - this can be expanded later
        flashcards = []
        response = JsonResponse({"flashcards": flashcards}, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        response = JsonResponse({"detail": str(e)}, status=400)
        response["Access-Control-Allow-Origin"] = "*"
        return response


@csrf_exempt
@require_http_methods(["POST", "OPTIONS"])
async def session_message_view(request: HttpRequest, session_id: int) -> JsonResponse:
    """
    Handle audio message in a session - COMPLETE FLOW
    """
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
    
    try:
        logger.info(f"=== COMPLETE FLOW: Starting message processing for session {session_id} ===")
        
        # Get user
        user = await _get_user_from_request(request)
        if not user:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        
        # Get session
        try:
            session = await VoiceSession.objects.select_related('user').aget(id=session_id)
            if session.user.id != user.id:
                return JsonResponse({"detail": "Access denied"}, status=403)
        except VoiceSession.DoesNotExist:
            return JsonResponse({"detail": "Session not found"}, status=404)
        
        # Check audio file
        if 'audio' not in request.FILES:
            return JsonResponse({"detail": "Audio file is required"}, status=400)
        
        audio_file = request.FILES['audio']
        if not audio_file:
            return JsonResponse({"detail": "Audio file cannot be empty"}, status=400)
        
        # Read audio
        audio_bytes = audio_file.read()
        logger.info(f"Audio received: {len(audio_bytes)} bytes")
        
        # Step 1: Transcribe and assess pronunciation with Azure
        logger.info("Step 1: Starting Azure transcription")
        content_type = audio_file.content_type if hasattr(audio_file, 'content_type') else 'audio/webm'
        logger.info(f"Audio content type: {content_type}")
        logger.info(f"Audio file name: {audio_file.name}")
        logger.info(f"Audio size: {len(audio_bytes)} bytes")
        
        # Validate audio data before sending to Azure
        if len(audio_bytes) < 1000:
            logger.error(f"Audio file too small: {len(audio_bytes)} bytes")
            return JsonResponse({
                "detail": "Audio file is too small or empty. Please record again.",
                "reply_text": "",
                "reply_audio_url": "",
                "corrections": [],
                "new_flashcards": [],
                "pronunciation": {"overall_score": 0.0, "word_scores": []}
            }, status=400)
        
        try:
            azure_result = await recognize_and_assess(
                wav_bytes=audio_bytes,
                key=os.getenv('AZURE_SPEECH_KEY'),
                region=os.getenv('AZURE_SPEECH_REGION'),
                language=os.getenv('AZURE_SPEECH_LANGUAGE', 'en-US'),
                timeout_s=20.0,
                content_type=content_type
            )
            logger.info(f"Azure transcription completed: '{azure_result.transcript}'")
        except Exception as e:
            logger.error(f"Azure transcription failed: {str(e)}")
            return JsonResponse({
                "detail": "Audio processing failed. The audio format may not be supported. Please try recording again.",
                "reply_text": "",
                "reply_audio_url": "",
                "corrections": [],
                "new_flashcards": [],
                "pronunciation": {"overall_score": 0.0, "word_scores": []}
            }, status=400)
        
        # Step 2: Get session history
        logger.info("Step 2: Getting session history")
        session_messages = await _get_session_history(session, limit=10)
        logger.info(f"Session history: {len(session_messages)} messages")
        
        # Step 3: Get tutor response from Groq
        logger.info(f"Step 3: Getting tutor response for: {azure_result.transcript[:100]}...")
        tutor_response = await groq_client.get_tutor_response(
            user_message=azure_result.transcript,
            session_history=session_messages
        )
        logger.info("Tutor response received successfully")
        
        # Step 4: Generate TTS audio
        logger.info("Step 4: Generating TTS audio")
        tts_audio_bytes = await synthesize_tts(
            text=tutor_response.get('reply_text', ''),
            key=os.getenv('AZURE_SPEECH_KEY'),
            region=os.getenv('AZURE_SPEECH_REGION'),
            voice=os.getenv('AZURE_SPEECH_VOICE', 'en-US-JennyNeural'),
            timeout_s=15.0
        )
        logger.info(f"TTS audio generated: {len(tts_audio_bytes)} bytes")
        
        # Step 5: Save TTS audio
        reply_audio_url = ""
        if tts_audio_bytes:
            reply_audio_url = await _save_tts_audio(tts_audio_bytes)
            logger.info(f"TTS audio saved: {reply_audio_url}")
        
        # Step 6: Save messages and create flashcards
        logger.info("Step 6: Saving messages and creating flashcards")
        await _save_session_interaction(
            session=session,
            user_message=azure_result.transcript,
            tutor_response=tutor_response.get('reply_text', ''),
            pronunciation_score=azure_result.overall_score,
            word_scores=azure_result.word_scores
        )
        logger.info("Messages and flashcards saved successfully")
        
        # Step 7: Return complete response
        logger.info("Step 7: Returning complete response")
        response_data = {
            "detail": "Success",
            "reply_text": tutor_response.get('reply_text', ''),
            "reply_audio_url": reply_audio_url,
            "corrections": [
                {
                    "word": ws.word,
                    "correction": ws.word,
                    "accuracy_score": ws.accuracy_score
                }
                for ws in azure_result.word_scores if ws.accuracy_score is not None
            ],
            "new_flashcards": [
                {"front": ws.word, "back": ws.word}
                for ws in azure_result.word_scores if ws.accuracy_score and ws.accuracy_score < 85
            ][:3],
            "pronunciation": {
                "overall_score": azure_result.overall_score or 0.0,
                "word_scores": [
                    {
                        "word": ws.word,
                        "accuracy_score": ws.accuracy_score or 0.0,
                        "error_type": ws.error_type
                    }
                    for ws in azure_result.word_scores
                ]
            }
        }
        
        response = JsonResponse(response_data)
        response["Access-Control-Allow-Origin"] = "*"
        logger.info("=== COMPLETE FLOW: SUCCESS ===")
        return response
        
    except Exception as e:
        logger.error(f"=== COMPLETE FLOW ERROR: {str(e)} ===")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        
        response = JsonResponse({
            "detail": "An error occurred processing your message. Please try again.",
            "reply_text": "",
            "reply_audio_url": "",
            "corrections": [],
            "new_flashcards": [],
            "pronunciation": {"overall_score": 0.0, "word_scores": []}
        }, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response
    """
    Handle audio message in a session
    
    Flow:
    1. Receive audio file
    2. Transcribe and assess pronunciation with Azure
    3. Get session history and send to Groq with tutor prompt
    4. Generate TTS audio for response
    5. Save messages and create flashcards
    6. Return structured response
    """
    if request.method == "OPTIONS":
        response = JsonResponse({"detail": "OK"})
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = "POST, OPTIONS"
        response["Access-Control-Allow-Headers"] = "Content-Type, Accept"
        return response
    
    try:
        # Get user from JWT token (simplified - in production, use proper auth)
        user = await _get_user_from_request(request)
        if not user:
            return JsonResponse({"detail": "Authentication required"}, status=401)
        
        # Get session
        try:
            session = await VoiceSession.objects.select_related('user').aget(id=session_id)
            if session.user.id != user.id:
                return JsonResponse({"detail": "Access denied"}, status=403)
        except VoiceSession.DoesNotExist:
            return JsonResponse({"detail": "Session not found"}, status=404)
        
        # Check if audio file is provided
        if 'audio' not in request.FILES:
            return JsonResponse({"detail": "Audio file is required"}, status=400)
        
        audio_file = request.FILES['audio']
        if not audio_file:
            return JsonResponse({"detail": "Audio file cannot be empty"}, status=400)
        
        # Read audio file bytes
        audio_bytes = audio_file.read()
        
        # Audio conversion is handled internally by recognize_and_assess function
        logger.info(f"Audio received for processing: {len(audio_bytes)} bytes")
        
        # Step 1: Transcribe and assess pronunciation
        logger.info(f"Starting transcription for session {session_id}")
        
        try:
            # Transcribe and assess pronunciation with Azure
            logger.info("Starting Azure transcription")
            content_type = audio_file.content_type if hasattr(audio_file, 'content_type') else 'audio/webm'
            logger.info(f"Audio content type: {content_type}")
            
            azure_result = await recognize_and_assess(
                wav_bytes=audio_bytes,
                key=os.getenv('AZURE_SPEECH_KEY'),
                region=os.getenv('AZURE_SPEECH_REGION'),
                language=os.getenv('AZURE_SPEECH_LANGUAGE', 'en-US'),
                timeout_s=20.0,
                content_type=content_type
            )
            logger.info(f"Azure transcription completed: '{azure_result.transcript}'")
        except Exception as e:
            logger.error(f"Error in Azure transcription: {str(e)}")
            raise
        
        if azure_result.transcript == "":
            return JsonResponse({
                "detail": "Could not transcribe audio. Please try speaking more clearly.",
                "reply_text": "",
                "reply_audio_url": "",
                "corrections": [],
                "new_flashcards": [],
                "pronunciation": {
                    "overall_score": 0.0,
                    "word_scores": []
                }
            }, status=400)
        
        # Step 2: Get session history (last 10 messages)
        try:
            logger.info("Step 2: Getting session history")
            session_messages = await _get_session_history(session, limit=10)
            logger.info(f"Session history retrieved: {len(session_messages)} messages")
        except Exception as e:
            logger.error(f"Error getting session history: {str(e)}")
            raise
        
        # Step 3: Get tutor response from Groq
        try:
            logger.info(f"Step 3: Getting tutor response for: {azure_result.transcript[:100]}...")
            tutor_response = await groq_client.get_tutor_response(
                user_message=azure_result.transcript,
                session_history=session_messages
            )
            logger.info("Tutor response received successfully")
        except Exception as e:
            logger.error(f"Error getting tutor response: {str(e)}")
            raise
        
        # Step 4: Generate TTS audio for response
        try:
            logger.info("Step 4: Generating TTS audio for tutor response")
            tts_audio_bytes = await synthesize_tts(
                text=tutor_response.get('reply_text', ''),
                key=os.getenv('AZURE_SPEECH_KEY'),
                region=os.getenv('AZURE_SPEECH_REGION'),
                voice=os.getenv('AZURE_SPEECH_VOICE', 'en-US-JennyNeural'),
                timeout_s=15.0
            )
            logger.info("TTS audio generated successfully")
        except Exception as e:
            logger.error(f"Error generating TTS audio: {str(e)}")
            raise
        
        # Save TTS audio and get URL
        reply_audio_url = ""
        if tts_audio_bytes:
            reply_audio_url = await _save_tts_audio(tts_audio_bytes)
        
        # Step 5: Save messages and create flashcards
        logger.info("Saving messages and creating flashcards")
        
        await _save_session_interaction(
            session=session,
            user_transcript=azure_result.transcript,
            assistant_text=tutor_response.get('reply_text', ''),
            reply_audio_url=reply_audio_url,
            pronunciation_score=azure_result.overall_score,
            corrections=tutor_response.get('corrections', []),
            vocab_suggestions=tutor_response.get('vocab_suggestions', [])
        )
        
        # Step 6: Return structured response
        response_data = {
            "transcript": azure_result.transcript,
            "reply_text": tutor_response.get('reply_text', ''),
            "reply_audio_url": reply_audio_url,
            "corrections": tutor_response.get('corrections', []),
            "new_flashcards": tutor_response.get('vocab_suggestions', []),
            "pronunciation": {
                "overall_score": azure_result.overall_score or 0.0,
                "accuracy_score": azure_result.accuracy_score or 0.0,
                "fluency_score": azure_result.fluency_score or 0.0,
                "completeness_score": azure_result.completeness_score or 0.0,
                "word_scores": [
                    {
                        "word": ws.word,
                        "accuracy_score": ws.accuracy_score,
                        "error_type": ws.error_type
                    }
                    for ws in azure_result.word_scores
                ]
            }
        }
        
        response = JsonResponse(response_data, status=200)
        response["Access-Control-Allow-Origin"] = "*"
        return response
        
    except Exception as e:
        logger.error(f"Error in session_message_view: {str(e)}")
        response = JsonResponse({
            "detail": "An error occurred processing your message. Please try again.",
            "reply_text": "",
            "reply_audio_url": "",
            "corrections": [],
            "new_flashcards": [],
            "pronunciation": {
                "overall_score": 0.0,
                "word_scores": []
            }
        }, status=500)
        response["Access-Control-Allow-Origin"] = "*"
        return response


# Helper functions

def _get_user_from_request_sync(request: HttpRequest) -> User | None:
    """Extract user from JWT token (simplified implementation)"""
    try:
        # In production, use proper JWT validation
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        # For now, just return first user (implement proper JWT validation)
        return User.objects.first()
    except Exception:
        return None

async def _get_user_from_request(request: HttpRequest) -> User | None:
    """Extract user from JWT token (simplified implementation)"""
    try:
        # In production, use proper JWT validation
        auth_header = request.headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return None
        
        token = auth_header[7:]  # Remove 'Bearer '
        
        # For now, just return first user (implement proper JWT validation)
        return await User.objects.afirst()
    except Exception:
        return None


async def _get_session_history(session: VoiceSession, limit: int = 10) -> list[Dict[str, str]]:
    """Get formatted session history for LLM context"""
    from asgiref.sync import sync_to_async
    
    def _get_messages_sync():
        return list(SessionMessage.objects.filter(
            session=session
        ).order_by('created_at').select_related('session')[:limit])
    
    messages = await sync_to_async(_get_messages_sync)()
    
    history = []
    for msg in messages:
        history.append({
            "role": msg.role,
            "content": msg.text
        })
    
    return history


async def _save_tts_audio(audio_bytes: bytes) -> str:
    """Save TTS audio and return URL"""
    try:
        filename = f"tts_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(audio_bytes) % 10000}.wav"
        file_path = os.path.join('tts', filename)
        
        # Ensure directory exists
        os.makedirs(os.path.join(settings.MEDIA_ROOT, 'tts'), exist_ok=True)
        
        # Save file
        default_storage.save(file_path, ContentFile(audio_bytes))
        
        return f"{settings.MEDIA_URL}tts/{filename}"
    except Exception as e:
        logger.error(f"Error saving TTS audio: {str(e)}")
        return ""


@transaction.atomic
async def _save_session_interaction(
    session: VoiceSession,
    user_transcript: str,
    assistant_text: str,
    reply_audio_url: str,
    pronunciation_score: float,
    corrections: list[str],
    vocab_suggestions: list[Dict[str, str]]
):
    """Save user message and assistant response, create flashcards"""
    try:
        # Save user message
        user_message = SessionMessage(
            session=session,
            role=SessionMessage.Role.USER,
            text=user_transcript,
            pronunciation_score=pronunciation_score
        )
        await user_message.asave()
        
        # Save assistant message
        assistant_message = SessionMessage(
            session=session,
            role=SessionMessage.Role.ASSISTANT,
            text=assistant_text,
            audio_url=reply_audio_url
        )
        await assistant_message.asave()
        
        # Create flashcards from vocabulary suggestions
        for vocab in vocab_suggestions:
            if vocab.get('front') and vocab.get('back'):
                flashcard = FlashCard(
                    user=session.user,
                    front=vocab['front'],
                    back=vocab['back'],
                    created_from_session=session
                )
                await flashcard.asave()
        
        # Update session stats
        session.total_messages += 1
        if not session.ended_at:
            session.ended_at = datetime.now()
        await session.asave()
        
        logger.info(f"Saved interaction for session {session.id}")
        
    except Exception as e:
        logger.error(f"Error saving session interaction: {str(e)}")
        raise
