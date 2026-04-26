#!/usr/bin/env python
import os
import sys
import django
import json
import requests

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings.dev')
django.setup()

from django.test import Client

def test_register():
    client = Client()
    
    data = {
        "username": "testuser123",
        "email": "test123@example.com", 
        "password": "testpass123"
    }
    
    print("Testing registration endpoint...")
    print(f"Data: {data}")
    
    response = client.post(
        '/api/auth/register/',
        data=json.dumps(data),
        content_type='application/json'
    )
    
    print(f"Status Code: {response.status_code}")
    print(f"Response: {response.content.decode()}")
    print(f"Headers: {dict(response.headers)}")
    
    return response

if __name__ == '__main__':
    test_register()
