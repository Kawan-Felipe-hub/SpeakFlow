#!/usr/bin/env python3
import requests
import json

def test_audio_upload_com_auth():
    base_url = "http://127.0.0.1:8000/api"
    
    # 1. Fazer login para obter token JWT
    print("=== FAZENDO LOGIN ===")
    login_data = {
        "username": "teste",  # seu usuário
        "password": "123456789"  # sua senha
    }
    
    try:
        login_response = requests.post(f"{base_url}/auth/login/", 
                                     json=login_data,
                                     headers={'Content-Type': 'application/json'})
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data['access']
            print(f"Login successful! Token: {access_token[:50]}...")
        else:
            print(f"Login failed: {login_response.status_code} - {login_response.text}")
            return
            
    except Exception as e:
        print(f"Erro no login: {e}")
        return
    
    # 2. Enviar áudio com autenticação
    print("\n=== ENVIANDO ÁUDIO ===")
    
    # Criar um arquivo de áudio falso (simulando o blob webm)
    fake_audio_content = b"fake_webm_audio_content_for_testing"
    
    # Preparar o FormData exatamente como o frontend envia
    files = {
        'audio': ('mensagem.webm', fake_audio_content, 'audio/webm')
    }
    
    # Headers com token de autenticação
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Accept': 'application/json',
    }
    
    try:
        print("Enviando requisição para:", f"{base_url}/sessions/27/message/")
        print("Arquivo de áudio:", len(fake_audio_content), "bytes")
        
        response = requests.post(f"{base_url}/sessions/27/message/", 
                               files=files, 
                               headers=headers)
        
        print(f"Status Code: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        try:
            print(f"Response: {response.json()}")
        except:
            print(f"Response Text: {response.text}")
            
    except Exception as e:
        print(f"Erro na requisição: {e}")

if __name__ == "__main__":
    test_audio_upload_com_auth()
