"""Главный urls."""
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('foodgram_api.urls')),
    path('api/', include('users.urls')),
]
