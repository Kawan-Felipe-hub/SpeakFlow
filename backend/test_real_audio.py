#!/usr/bin/env python3
import requests
import io
import wave
import struct

def create_fake_wav():
    """Create a minimal WAV file for testing"""
    sample_rate = 44100
    duration = 1.0  # 1 second
    frequency = 440  # A4 note
    
    num_samples = int(sample_rate * duration)
    
    # Create WAV file data
    wav_buffer = io.BytesIO()
    with wave.open(wav_buffer, 'wb') as wav_file:
        wav_file.setnchannels(1)  # Mono
        wav_file.setsampwidth(2)  # 16-bit
        wav_file.setframerate(sample_rate)
        
        # Generate sine wave
        for i in range(num_samples):
            value = int(32767 * 0.1 * (i % 100) / 100)  # Simple wave
            wav_file.writeframes(struct.pack('<h', value))
    
    wav_buffer.seek(0)
    return wav_buffer.read()

def test_with_real_audio():
    # Login
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    login_data = {"username": "test", "password": "testpass"}
    
    login_response = requests.post(login_url, json=login_data)
    if login_response.status_code != 200:
        print("Login failed:", login_response.text)
        return
    
    token = login_response.json().get("access")
    
    # Create real WAV audio
    wav_data = create_fake_wav()
    print(f"Created WAV file: {len(wav_data)} bytes")
    
    # Send message
    url = "http://127.0.0.1:8000/api/sessions/27/message/"
    files = {
        'audio': ('message.wav', wav_data, 'audio/wav')
    }
    headers = {
        'Authorization': f'Bearer {token}',
        'Accept': 'application/json',
    }
    
    print("Sending audio with WAV format...")
    response = requests.post(url, files=files, headers=headers)
    
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response JSON: {response.json()}")
    except:
        print(f"Response Text: {response.text}")

if __name__ == "__main__":
    test_with_real_audio()
