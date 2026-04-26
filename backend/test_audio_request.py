#!/usr/bin/env python3
import requests
import json
from pathlib import Path

def test_audio_upload():
    # URL da API
    url = "http://127.0.0.1:8000/api/sessions/27/message/"
    
    # Criar um arquivo de áudio falso (simulando o blob webm)
    fake_audio_content = b"fake_webm_audio_content_for_testing"
    
    # Preparar o FormData exatamente como o frontend envia
    files = {
        'audio': ('mensagem.webm', fake_audio_content, 'audio/webm')
    }
    
    # Headers (simulando o frontend)
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'multipart/form-data',
    }
    
    try:
        print("Enviando requisição para:", url)
        print("Arquivo de áudio:", len(fake_audio_content), "bytes")
        
        response = requests.post(url, files=files, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_audio_upload()
