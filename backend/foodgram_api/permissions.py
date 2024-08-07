from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """Класс обычного разрешения."""

    def has_permission(self, request, view):
        """Логика запроса."""
        return (
            request.method in permissions.SAFE_METHODS
            or request.user and request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Логика ввода."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.author == request.user


class IsАOrReadOnly(permissions.BasePermission):
    """Класс разрешений автора."""

    def has_permission(self, request, view):
        """Логика запроса."""
        return (
            request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        """Логика ввода."""
        return obj.user == request.user
