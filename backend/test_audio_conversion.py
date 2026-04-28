#!/usr/bin/env python3
"""
Test script to verify WebM to WAV conversion for Azure Speech
"""

import os
import sys
import asyncio
import logging
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings')
import django
django.setup()

from core.integrations.azure_speech import recognize_and_assess, _convert_webm_to_wav

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def test_conversion():
    """Test WebM to WAV conversion and Azure transcription"""
    
    # Check environment variables
    azure_key = os.getenv('AZURE_SPEECH_KEY')
    azure_region = os.getenv('AZURE_SPEECH_REGION')
    
    if not azure_key or not azure_region:
        logger.error("Missing Azure Speech credentials. Please check your .env file.")
        return False
    
    logger.info("=== Testing WebM to WAV Conversion ===")
    
    # Look for test audio files
    test_files = [
        "mensagem.webm",
        "test_audio.webm", 
        "sample.webm"
    ]
    
    test_audio_path = None
    for filename in test_files:
        if os.path.exists(filename):
            test_audio_path = filename
            break
    
    if not test_audio_path:
        # Create a mock WebM file for testing
        logger.warning("No test audio file found. Creating a mock WebM file...")
        mock_audio = b'WEBM_MOCK_DATA_FOR_TESTING' * 1000  # ~25KB mock data
        test_audio_path = "mock_test.webm"
        with open(test_audio_path, 'wb') as f:
            f.write(mock_audio)
        logger.info(f"Created mock file: {test_audio_path}")
    
    try:
        # Read the audio file
        with open(test_audio_path, 'rb') as f:
            audio_bytes = f.read()
        
        logger.info(f"Audio file loaded: {len(audio_bytes)} bytes")
        
        # Test conversion function
        logger.info("Testing conversion function...")
        converted_bytes = _convert_webm_to_wav(audio_bytes, "audio/webm")
        logger.info(f"Conversion result: {len(converted_bytes)} bytes")
        
        # Test full Azure transcription
        logger.info("Testing Azure transcription...")
        result = await recognize_and_assess(
            wav_bytes=audio_bytes,
            key=azure_key,
            region=azure_region,
            language="en-US",
            timeout_s=20.0,
            content_type="audio/webm"
        )
        
        logger.info(f"Transcription result:")
        logger.info(f"  Transcript: '{result.transcript}'")
        logger.info(f"  Overall Score: {result.overall_score}")
        logger.info(f"  Word Count: {len(result.word_scores)}")
        
        if result.transcript and result.transcript.strip():
            logger.success("✅ Transcription successful!")
            return True
        else:
            logger.warning("⚠️ Empty transcript - may indicate format issue")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        return False
    
    finally:
        # Cleanup mock file if created
        if test_audio_path == "mock_test.webm" and os.path.exists(test_audio_path):
            os.remove(test_audio_path)
            logger.info("Cleaned up mock file")

if __name__ == "__main__":
    print("🎵 Audio Conversion Test")
    print("=" * 50)
    
    success = asyncio.run(test_conversion())
    
    if success:
        print("\n✅ Test completed successfully!")
    else:
        print("\n❌ Test failed. Check logs above.")
    
    print("=" * 50)
