from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse


class CustomCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add CORS headers to all responses
        origin = request.headers.get("Origin")
        
        # Check if origin is in allowed list
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        if origin and (origin in allowed_origins or settings.CORS_ALLOW_ALL_ORIGINS):
            response["Access-Control-Allow-Origin"] = origin
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
            response["Access-Control-Max-Age"] = "86400"
        
        # Handle preflight requests
        if request.method == "OPTIONS":
            response = HttpResponse()
            if origin and (origin in allowed_origins or settings.CORS_ALLOW_ALL_ORIGINS):
                response["Access-Control-Allow-Origin"] = origin
                response["Access-Control-Allow-Credentials"] = "true"
                response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD"
                response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
                response["Access-Control-Max-Age"] = "86400"
        
        return response
