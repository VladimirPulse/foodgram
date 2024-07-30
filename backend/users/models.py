"""Модуль пользователя."""
from django.contrib.auth.models import AbstractUser
from django.db import models


class MyUser(AbstractUser):
    """Класс пользователя."""

    is_subscribed = models.BooleanField('Подписан', default=False)
