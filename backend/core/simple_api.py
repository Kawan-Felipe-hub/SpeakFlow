from __future__ import annotations

from django.http import JsonResponse, HttpRequest
from django.contrib.auth import authenticate
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from rest_framework_simplejwt.tokens import RefreshToken
import json

from core.models import User


# Middleware para logar todas as requisições
class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        print(f"\n=== {request.method} {request.path} ===")
        print(f"Headers: {dict(request.headers)}")
        print(f"Body: {request.body}")
        print(f"Origin: {request.headers.get('Origin', 'None')}")
        
        response = self.get_response(request)
        
        print(f"Response Status: {response.status_code}")
        print(f"Response Headers: {dict(response.headers) if hasattr(response, 'headers') else 'No headers'}")
        print("=== END ===\n")
        
        return response


def issue_tokens(user: User) -> dict:
    refresh = RefreshToken.for_user(user)
    return {
        "access": str(refresh.access_token),
        "refresh": str(refresh)
    }


@csrf_exempt
@require_http_methods(["POST"])
def register(request: HttpRequest) -> JsonResponse:
    try:
        print(f"Request body: {request.body}")
        print(f"Request headers: {dict(request.headers)}")
        
        data = json.loads(request.body)
        print(f"Parsed data: {data}")
        
        username = data.get("username")
        email = data.get("email")
        password = data.get("password")
        
        print(f"Username: {username}, Email: {email}, Password: {'*' * len(password) if password else 'None'}")
        
        if not username or not email or not password:
            return JsonResponse({"detail": "Username, email and password are required"}, status=400)
        
        if User.objects.filter(username=username).exists():
            return JsonResponse({"detail": "Username already exists."}, status=400)
            
        if User.objects.filter(email=email).exists():
            return JsonResponse({"detail": "Email already exists."}, status=400)
        
        user = User(username=username, email=email)
        user.set_password(password)
        user.save()
        
        tokens = issue_tokens(user)
        print(f"Tokens generated: {list(tokens.keys())}")
        
        return JsonResponse(tokens, status=201)
        
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return JsonResponse({"detail": f"Invalid JSON: {str(e)}"}, status=400)
    except Exception as e:
        print(f"Registration error: {e}")
        return JsonResponse({"detail": str(e)}, status=400)


@csrf_exempt
@require_http_methods(["POST"])
def login(request: HttpRequest) -> JsonResponse:
    try:
        data = json.loads(request.body)
        username = data.get("username")
        password = data.get("password")
        
        if not username or not password:
            return JsonResponse({"detail": "Username and password are required"}, status=400)
        
        user = authenticate(request, username=username, password=password)
        if user is None:
            return JsonResponse({"detail": "Invalid credentials."}, status=401)
            
        return JsonResponse(issue_tokens(user), status=200)
        
    except Exception as e:
        return JsonResponse({"detail": str(e)}, status=400)
