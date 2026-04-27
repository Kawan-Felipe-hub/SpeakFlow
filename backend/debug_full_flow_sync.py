#!/usr/bin/env python3
import os
import io
import wave
import struct
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings.dev')
import django
django.setup()

from core.integrations.azure_speech import recognize_and_assess, synthesize_tts
from core.integrations.groq_llm import tutor_reply
from core.models import VoiceSession, SessionMessage, FlashCard, User
from django.db import transaction
from django.core.files.storage import default_storage
from django.conf import settings
from asgiref.sync import sync_to_async

def create_fake_wav():
    """Create a minimal WAV file for testing"""
    sample_rate = 44100
    duration = 1.0
    num_samples = int(sample_rate * duration)
    
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)
        wav_file.setsampwidth(2)
        wav_file.setframerate(sample_rate)
        
        for i in range(num_samples):
            value = int(32767 * 0.1 * (i % 100) / 100)
            wav_file.writeframes(struct.pack('<h', value))
    
    wav_buffer.seek(0)
    return wav_buffer.read()

class FakeUploadedFile:
    def __init__(self, data, name):
        self.data = data
        self.name = name
    
    def read(self):
        return self.data

async def debug_full_flow():
    try:
        print("=== INICIANDO DEBUG DO FLUXO COMPLETO ===")
        
        # 1. Setup (usando sync_to_async)
        print("\n=== 1. SETUP ===")
        user = await sync_to_async(User.objects.first)()
        session = await sync_to_async(lambda: VoiceSession.objects.filter(id=27, user=user).first())()
        print(f"Session: {session}")
        
        # 2. Audio processing
        print("\n=== 2. PROCESSAMENTO DE ÁUDIO ===")
        wav_bytes = create_fake_wav()
        print(f"Áudio criado: {len(wav_bytes)} bytes")
        
        # 3. Azure STT
        print("\n=== 3. AZURE STT ===")
        try:
            stt_res = await recognize_and_assess(
                wav_bytes=wav_bytes,
                key=os.environ.get('AZURE_SPEECH_KEY'),
                region='brazilsouth',
                language='en-US',
                timeout_s=20,
            )
            print(f"STT OK: transcript='{stt_res.transcript}'")
        except Exception as e:
            print(f"ERRO NO STT: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 4. System prompt
        print("\n=== 4. SYSTEM PROMPT ===")
        try:
            system_prompt = (Path(settings.BASE_DIR) / "prompts" / "tutor_system.txt").read_text(encoding="utf-8")
            print(f"Prompt lido: {len(system_prompt)} chars")
        except Exception as e:
            print(f"ERRO NO PROMPT: {e}")
            return
        
        # 5. Groq LLM
        print("\n=== 5. GROQ LLM ===")
        try:
            llm = await tutor_reply(
                api_key=os.environ.get('GROQ_API_KEY'),
                model='llama-3.3-70b-versatile',
                system_prompt=system_prompt,
                history=[],
                transcript=stt_res.transcript,
                topic='General Conversation',
            )
            print(f"LLM OK: reply='{llm.reply_text}'")
        except Exception as e:
            print(f"ERRO NO LLM: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 6. TTS
        print("\n=== 6. TTS ===")
        try:
            tts_bytes = await synthesize_tts(
                text=llm.reply_text or "Hello",
                key=os.environ.get('AZURE_SPEECH_KEY'),
                region='brazilsouth',
                voice='en-US-JennyNeural',
                timeout_s=20,
            )
            print(f"TTS OK: {len(tts_bytes)} bytes")
        except Exception as e:
            print(f"ERRO NO TTS: {e}")
            import traceback
            traceback.print_exc()
            return
        
        # 7. Persistência
        print("\n=== 7. PERSISTÊNCIA ===")
        try:
            def _persist_and_create():
                with transaction.atomic():
                    user_msg = SessionMessage.objects.create(
                        session=session,
                        role=SessionMessage.Role.USER,
                        text=stt_res.transcript,
                        audio_url="",
                        pronunciation_score={},
                    )
                    print(f"User message criada: {user_msg.id}")
                    
                    assistant_msg = SessionMessage.objects.create(
                        session=session,
                        role=SessionMessage.Role.ASSISTANT,
                        text=llm.reply_text,
                        audio_url="",
                        pronunciation_score={},
                    )
                    print(f"Assistant message criada: {assistant_msg.id}")
                    
                    # Rollback para não poluir
                    raise Exception("Rollback test")
            
            await sync_to_async(_persist_and_create)()
            print("Persistência OK (rollback)")
                
        except Exception as e:
            if "Rollback test" in str(e):
                print("Persistência OK (rollback)")
            else:
                print(f"ERRO NA PERSISTÊNCIA: {e}")
                import traceback
                traceback.print_exc()
                return
        
        print("\n=== FLUXO COMPLETO OK ===")
        
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    import asyncio
    asyncio.run(debug_full_flow())
