#!/usr/bin/env python3
"""
Test the new robust WebM to WAV conversion
"""

import os
import sys
import asyncio

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings')
import django
django.setup()

from core.integrations.azure_speech import recognize_and_assess

async def test_new_conversion():
    """Test the new robust conversion system"""
    
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_region = os.getenv('AZURE_SPEECH_REGION')
    
    print("🧪 Testing New WebM Conversion System")
    print("=" * 50)
    
    # Test 1: Invalid WebM (should trigger fallback)
    print("\n📛 Test 1: Invalid WebM Data")
    try:
        invalid_webm = b'INVALID_WEBM_DATA' * 1000
        print(f"Data size: {len(invalid_webm)} bytes")
        
        result = await recognize_and_assess(
            wav_bytes=invalid_webm,
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/webm'
        )
        print(f"✅ Result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 2: Empty WebM header (should trigger fallback)
    print("\n📛 Test 2: Empty WebM Header")
    try:
        empty_header = b'\x00\x00\x00\x00' + b'FAKE_AUDIO' * 500
        print(f"Data size: {len(empty_header)} bytes")
        
        result = await recognize_and_assess(
            wav_bytes=empty_header,
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/webm'
        )
        print(f"✅ Result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    # Test 3: Valid WebM header but fake data
    print("\n📛 Test 3: Valid WebM Header + Fake Data")
    try:
        valid_header = b'\x1a\x45\xdf\xa3' + b'WEBM_HEADER' * 10
        fake_audio = b'FAKE_AUDIO_DATA' * 1000
        webm_like = valid_header + fake_audio
        print(f"Data size: {len(webm_like)} bytes")
        
        result = await recognize_and_assess(
            wav_bytes=webm_like,
            key=azure_key,
            region=azure_region,
            language='en-US',
            content_type='audio/webm'
        )
        print(f"✅ Result: '{result.transcript}' (Score: {result.overall_score})")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    print("\n" + "=" * 50)
    print("🏁 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_new_conversion())
