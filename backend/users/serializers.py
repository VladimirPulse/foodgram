from django.contrib.auth import get_user_model
from django.contrib.auth.validators import UnicodeUsernameValidator
from djoser.serializers import UserCreateSerializer
from rest_framework import serializers
from rest_framework.validators import UniqueValidator

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер пользователя."""

    class Meta:
        """Настройка."""

        model = User
        fields = ['email', 'username', 'id', 'first_name', 'last_name']


class CustomUserCreateSerializer(UserCreateSerializer):
    """Сериалайзер кастомного пользователя."""

    email = serializers.EmailField(
        max_length=254,
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        max_length=150,
        required=True,
        validators=[
            UnicodeUsernameValidator(),
            UniqueValidator(queryset=User.objects.all())
        ]
    )
    first_name = serializers.CharField(max_length=150, required=True)
    last_name = serializers.CharField(max_length=150, required=True)

    class Meta(UserCreateSerializer.Meta):
        """Настройка."""

        fields = [
            'id',
            'password',
            'email',
            'username',
            'first_name',
            'last_name'
        ]


class UserSelfSerializer(serializers.ModelSerializer):
    """Сериализатор для личного профиля."""

    is_subscribed = serializers.BooleanField()

    class Meta:
        """Тонкая настройка."""

        model = User
        fields = (
            'id',
            'is_subscribed',
            'email',
            'username',
            'first_name',
            'last_name'
        )
