#!/usr/bin/env python3
"""
Test with real WebM audio from browser recording
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings')
import django
django.setup()

from core.integrations.azure_speech import recognize_and_assess

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_real_webm():
    """Create a more realistic WebM-like file"""
    # WebM header with EBML structure
    webm_header = b'\x1a\x45\xdf\xa3'  # EBML header
    webm_header += b'\x01\x00\x00\x00'  # Version
    webm_header += b'\x42\x82'  # DocType
    webm_header += b'\x88'  # DocType length (8 chars)
    webm_header += b'webm' + b'\x00\x00\x00'  # "webm" + padding
    
    # Add some mock audio data
    audio_data = b'MOCK_WEBM_AUDIO_DATA' * 1000
    
    return webm_header + audio_data

async def test_webm_scenarios():
    """Test different WebM scenarios"""
    
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_region = os.getenv('AZURE_SPEECH_REGION')
    
    if not azure_key:
        logger.error("❌ Missing AZURE_SPEECH_KEY")
        return
    
    logger.info("🎵 Testing WebM scenarios...")
    
    # Scenario 1: Perfect WAV (should work)
    logger.info("\n=== Test 1: Perfect WAV ===")
    try:
        import wave
        import struct
        
        wav_buffer = bytearray()
        # WAV header
        wav_buffer.extend(b'RIFF')
        wav_buffer.extend((36 + 16000).to_bytes(4, 'little'))  # File size
        wav_buffer.extend(b'WAVE')
        wav_buffer.extend(b'fmt ')
        wav_buffer.extend((16).to_bytes(4, 'little'))  # Chunk size
        wav_buffer.extend((1).to_bytes(2, 'little'))   # Audio format (PCM)
        wav_buffer.extend((1).to_bytes(2, 'little'))   # Channels
        wav_buffer.extend((16000).to_bytes(4, 'little'))  # Sample rate
        wav_buffer.extend((32000).to_bytes(4, 'little'))  # Byte rate
        wav_buffer.extend((2).to_bytes(2, 'little'))   # Block align
        wav_buffer.extend((16).to_bytes(2, 'little'))  # Bits per sample
        wav_buffer.extend(b'data')
        wav_buffer.extend((16000).to_bytes(4, 'little'))  # Data size
        
        # Add some audio data
        for i in range(8000):  # 8000 samples = 0.5 seconds
            sample = int(32767 * 0.1 * (i % 100) / 100)  # Small sine wave
            wav_buffer.extend(sample.to_bytes(2, 'little', signed=True))
        
        result = await recognize_and_assess(
            wav_bytes=bytes(wav_buffer),
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/wav'
        )
        logger.info(f"✅ WAV result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        logger.error(f"❌ WAV failed: {e}")
    
    # Scenario 2: Mock WebM (like browser recording)
    logger.info("\n=== Test 2: Mock WebM ===")
    try:
        webm_data = create_real_webm()
        logger.info(f"Created mock WebM: {len(webm_data)} bytes")
        
        result = await recognize_and_assess(
            wav_bytes=webm_data,
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/webm'
        )
        logger.info(f"✅ WebM result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        logger.error(f"❌ WebM failed: {e}")
    
    # Scenario 3: Empty/invalid data
    logger.info("\n=== Test 3: Invalid WebM ===")
    try:
        invalid_data = b'INVALID_AUDIO_DATA' * 10
        
        result = await recognize_and_assess(
            wav_bytes=invalid_data,
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/webm'
        )
        logger.info(f"✅ Invalid result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        logger.error(f"❌ Invalid failed: {e}")

if __name__ == "__main__":
    print("🧪 Real WebM Test")
    print("=" * 50)
    
    asyncio.run(test_webm_scenarios())
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")
