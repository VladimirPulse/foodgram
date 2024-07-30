"""Модуль админки пользователя."""
from django.contrib import admin

from .models import MyUser


@admin.register(MyUser)
class RecipeAdmin(admin.ModelAdmin):
    """Класс админки пользователя."""

    list_display = (
        'email',
        'username',
        'first_name',
        'last_name',
        'is_subscribed',
        'is_staff',
    )
    list_filter = ('first_name', 'email', )
    search_fields = ('first_name', )
