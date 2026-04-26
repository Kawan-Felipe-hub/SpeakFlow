#!/usr/bin/env python3
import os
import sys

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings.dev')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import django
django.setup()

from ninja.files import UploadedFile
from django.core.files.uploadedfile import SimpleUploadedFile
from core.api import post_message
from django.http import HttpRequest
from unittest.mock import Mock

def test_direct_api_call():
    """Testa a chamada direta da função API"""
    
    print("=== TESTE DIRETO DA API ===")
    
    # Criar um mock de request
    request = Mock(spec=HttpRequest)
    request.user = Mock()
    request.user.is_authenticated = True
    request.user.id = 1
    
    # Criar um arquivo de áudio fake
    fake_audio = SimpleUploadedFile(
        "mensagem.webm", 
        b"fake_webm_audio_content_for_testing", 
        content_type="audio/webm"
    )
    
    print(f"Audio criado: {fake_audio.name}")
    print(f"Audio size: {fake_audio.size}")
    print(f"Audio type: {fake_audio.content_type}")
    
    try:
        import asyncio
        
        async def run_test():
            try:
                result = await post_message(
                    request=request,
                    session_id=27,
                    audio=fake_audio,
                    text=None
                )
                print(f"Resultado: {result}")
                return result
            except Exception as e:
                print(f"ERRO NA CHAMADA DIRETA: {e}")
                import traceback
                traceback.print_exc()
                return None
        
        result = asyncio.run(run_test())
        
    except Exception as e:
        print(f"ERRO GERAL: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_direct_api_call()
