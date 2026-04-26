#!/usr/bin/env python3
"""
Script para testar o erro de WebM vs Azure Speech SDK
"""

import requests
import json
import io
from django.core.files.uploadedfile import SimpleUploadedFile
from core.integrations.azure_speech import recognize_and_assess

# Criar um áudio WebM de teste (simulado)
def create_test_webm():
    """Cria um blob WebM de teste para simular o frontend"""
    # Este é um WebM header muito básico para teste
    webm_header = b'\x1a\x45\xdf\xa3\xa3\x42\x86\x81\x01\x42\xf7\x81\x01\x42\xf2\x81\x04\x42\xf3\x81\x08\x42\x82\x84\x77\x65\x62\x6d\x42\x87\x81\x02\x42\x85\x81\x02\x18\x53\x80\x67\x01\x00\x00\x00\x00\x00'
    
    # Adiciona alguns dados de áudio falsos
    audio_data = b'\x00' * 1000  # 1KB de dados silenciosos
    
    return webm_header + audio_data

def test_webm_conversion():
    """Testa a conversão de WebM para WAV"""
    print("=== Testando conversão WebM para WAV ===")
    
    # Criar áudio de teste
    webm_bytes = create_test_webm()
    print(f"Áudio WebM criado: {len(webm_bytes)} bytes")
    
    # Testar conversão
    try:
        from core.integrations.azure_speech import _convert_webm_to_wav
        wav_bytes = _convert_webm_to_wav(webm_bytes, "audio/webm;codecs=opus")
        print(f"Conversão bem-sucedida: {len(wav_bytes)} bytes")
        return True
    except Exception as e:
        print(f"Erro na conversão: {e}")
        import traceback
        traceback.print_exc()
        return False

import asyncio

async def test_azure_speech_directly():
    """Testa diretamente com Azure Speech SDK"""
    print("\n=== Testando Azure Speech SDK diretamente ===")
    
    # Criar áudio de teste
    webm_bytes = create_test_webm()
    print(f"Áudio WebM criado: {len(webm_bytes)} bytes")
    
    # Tentar usar Azure Speech SDK diretamente
    try:
        # Simula os parâmetros que viriam das variáveis de ambiente
        key = "test_key"
        region = "test_region"
        language = "en-US"
        
        result = await recognize_and_assess(
            wav_bytes=webm_bytes,
            key=key,
            region=region,
            language=language,
            content_type="audio/webm;codecs=opus"
        )
        print(f"Sucesso: {result}")
        return True
    except Exception as e:
        print(f"Erro no Azure Speech SDK: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Iniciando testes de WebM para WAV...")
    
    # Teste 1: Conversão
    conversion_ok = test_webm_conversion()
    
    # Teste 2: Azure Speech SDK (async)
    azure_ok = asyncio.run(test_azure_speech_directly())
    
    print(f"\n=== Resultados ===")
    print(f"Conversão WebM->WAV: {'✅' if conversion_ok else '❌'}")
    print(f"Azure Speech SDK: {'✅' if azure_ok else '❌'}")
