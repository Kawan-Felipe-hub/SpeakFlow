#!/usr/bin/env python3
import requests
import json

def test_with_auth():
    # Primeiro, fazer login para obter token
    login_url = "http://127.0.0.1:8000/api/auth/login/"
    login_data = {
        "username": "test",  # Usuário existente
        "password": "testpass"
    }
    
    try:
        # Fazer login
        print("Fazendo login...")
        login_response = requests.post(login_url, json=login_data)
        print(f"Login status: {login_response.status_code}")
        
        if login_response.status_code != 200:
            print("Falha no login. Tentando criar usuário...")
            # Tentar criar usuário
            register_url = "http://127.0.0.1:8000/api/auth/register/"
            register_data = {
                "username": "testuser",
                "email": "test@example.com",
                "password": "testpass"
            }
            reg_response = requests.post(register_url, json=register_data)
            print(f"Register status: {reg_response.status_code}")
            
            if reg_response.status_code == 201:
                print("Usuário criado. Tentando login novamente...")
                login_response = requests.post(login_url, json=login_data)
        
        if login_response.status_code != 200:
            print(f"Erro no login: {login_response.text}")
            return
            
        token = login_response.json().get("access")
        print("Token obtido com sucesso!")
        
        # Agora testar o upload de áudio
        url = "http://127.0.0.1:8000/api/sessions/27/message/"
        
        fake_audio_content = b"fake_webm_audio_content_for_testing"
        files = {
            'audio': ('mensagem.webm', fake_audio_content, 'audio/webm')
        }
        
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/json',
        }
        
        print(f"\nEnviando áudio para sessão 27...")
        print(f"Authorization: Bearer {token[:20]}...")
        
        response = requests.post(url, files=files, headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
    except Exception as e:
        print(f"Erro: {e}")

if __name__ == "__main__":
    test_with_auth()
