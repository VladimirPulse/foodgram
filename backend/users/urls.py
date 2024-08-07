from django.urls import include, path
from rest_framework.routers import DefaultRouter

from users.views import PersonalProfileViewSet, UserViewSet

v1_router = DefaultRouter()

v1_router.register(r'users', UserViewSet, basename='users')

urlpatterns = [
    path(
        'users/me/',
        PersonalProfileViewSet.as_view(
            {'get': 'retrieve', 'patch': 'partial_update'}
        ),
        name='personal_profile',
    ),
    path(
        'users/set_password/',
        UserViewSet.as_view(
            {'post': 'set_password'}
        ), name='set_password'
    ),
    path('', include(v1_router.urls), name='api-root'),
    path('auth/', include('djoser.urls.authtoken'), name='token'),
]
