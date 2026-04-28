from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse, HttpResponse, Http404
from django.urls import path
from pathlib import Path

from core.api import api

def health_check(request):
    return JsonResponse({"status": "ok", "message": "SpeakFlow API is running"})

def serve_media(request, file_path):
    """Serve media files (audio files) directly."""
    try:
        # Security check - ensure the file path is safe
        if '..' in file_path or file_path.startswith('/'):
            raise Http404("Invalid file path")
        
        # Construct the full file path
        full_path = Path(settings.MEDIA_ROOT) / file_path
        
        # Check if file exists
        if not full_path.exists() or not full_path.is_file():
            print(f"File not found: {full_path}")
            raise Http404("File not found")
        
        # Determine content type based on file extension
        if file_path.endswith('.wav'):
            content_type = 'audio/wav'
        elif file_path.endswith('.mp3'):
            content_type = 'audio/mpeg'
        elif file_path.endswith('.webm'):
            content_type = 'audio/webm'
        else:
            content_type = 'application/octet-stream'
        
        # Read file and serve as response
        with open(full_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Length'] = full_path.stat().st_size
            response['Content-Disposition'] = f'inline; filename="{full_path.name}"'
            return response
            
    except Exception as e:
        print(f"Error serving media file {file_path}: {str(e)}")
        raise Http404("File not found")

urlpatterns = [
    path("", health_check),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
    path("api/media/<path:file_path>", serve_media),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

