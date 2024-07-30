"""Модуль apps."""
from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Класс приложения пользователя."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
