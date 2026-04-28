#!/usr/bin/env python3
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'speakflow.settings')
django.setup()

from core.models import User

def criar_usuario_teste():
    """Cria um usuário de teste para testar a API"""
    
    # Verificar se usuário já existe
    if User.objects.filter(username='teste').exists():
        print("Usuário 'teste' já existe!")
        user = User.objects.get(username='teste')
        print(f"ID: {user.id}, Email: {user.email}")
        return user
    
    # Criar novo usuário
    try:
        user = User.objects.create_user(
            username='teste',
            email='teste@example.com',
            password='senha123'
        )
        print(f"Usuário criado com sucesso!")
        print(f"Username: teste")
        print(f"Password: senha123")
        print(f"Email: {user.email}")
        print(f"ID: {user.id}")
        return user
    except Exception as e:
        print(f"Erro ao criar usuário: {e}")
        return None

if __name__ == "__main__":
    criar_usuario_teste()
