from __future__ import annotations

from django.conf import settings
from django.http import HttpResponse


class CustomCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Handle preflight requests first
        if request.method == "OPTIONS":
            response = HttpResponse()
            self._add_cors_headers(request, response)
            return response
        
        # Process normal request
        response = self.get_response(request)
        self._add_cors_headers(request, response)
        return response
    
    def _add_cors_headers(self, request, response):
        origin = request.headers.get("Origin")
        allowed_origins = getattr(settings, "CORS_ALLOWED_ORIGINS", [])
        allow_all = getattr(settings, "CORS_ALLOW_ALL_ORIGINS", False)
        
        # Always add CORS headers for development or if origin is allowed
        if not origin or origin in allowed_origins or allow_all:
            if origin:
                response["Access-Control-Allow-Origin"] = origin
            else:
                response["Access-Control-Allow-Origin"] = "*"
            response["Access-Control-Allow-Credentials"] = "true"
            response["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS, HEAD, PATCH"
            response["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With, Accept"
            response["Access-Control-Max-Age"] = "86400"
