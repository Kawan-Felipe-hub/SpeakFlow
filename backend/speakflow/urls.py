from __future__ import annotations

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import JsonResponse
from django.urls import path

from core.api import api

def health_check(request):
    return JsonResponse({"status": "ok", "message": "SpeakFlow API is running"})

urlpatterns = [
    path("", health_check),
    path("admin/", admin.site.urls),
    path("api/", api.urls),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

