#!/usr/bin/env python3
import requests
import json

def test_exact_frontend_request():
    """Simula exatamente como o frontend envia"""
    
    # Login exatamente como o frontend faz
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    login_data = {
        "username": "test",
        "password": "testpass"
    }
    
    print("=== LOGIN ===")
    login_response = requests.post(login_url, json=login_data)
    print(f"Login status: {login_response.status_code}")
    
    if login_response.status_code != 200:
        print(f"Login failed: {login_response.text}")
        return
    
    token_data = login_response.json()
    access_token = token_data.get("access")
    refresh_token = token_data.get("refresh")
    
    print(f"Token: {access_token[:20]}...")
    
    # Simular localStorage (não necessário para o teste)
    
    # Agora enviar mensagem exatamente como o frontend
    url = "http://127.0.0.1:8000/api/sessions/27/message/"
    
    # Criar FormData exatamente como o frontend
    fake_audio_content = b"fake_webm_audio_content_for_testing"
    
    # Simular FormData.append('audio', audioBlob, 'mensagem.webm')
    files = {
        'audio': ('mensagem.webm', fake_audio_content, 'audio/webm')
    }
    
    # Headers exatamente como o frontend envia via axios
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
        # Content-Type é omitido para que requests possa definir multipart/form-data com boundary correto
    }
    
    print("\n=== ENVIANDO MENSAGEM ===")
    print(f"URL: {url}")
    print(f"Audio size: {len(fake_audio_content)} bytes")
    print(f"Audio type: audio/webm")
    print(f"Filename: mensagem.webm")
    
    try:
        response = requests.post(url, files=files, headers=headers)
        
        print(f"\nStatus Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")
        
        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except:
            print(f"Response Text: {response.text}")
            
        # Verificar se há headers específicos de erro
        if response.status_code == 500:
            print("\n=== ERRO 500 DETECTADO ===")
            print("Verificando logs do servidor...")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_exact_frontend_request()
