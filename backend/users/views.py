from http.client import BAD_REQUEST, NO_CONTENT, UNAUTHORIZED

from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (CustomUserCreateSerializer, UserSelfSerializer,
                          UserSerializer)

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """Класс представления пользователя."""

    queryset = User.objects.all()
    http_method_names = ['get', 'post']
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        """Обработка запросов."""
        if self.request.method == 'GET':
            return UserSerializer
        if self.request.method == 'POST':
            return CustomUserCreateSerializer

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        """Установка пароля."""
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if not new_password or not request.user.check_password(
                current_password):
            return Response(
                status=BAD_REQUEST,
                data={'message': 'Вы ввели неверные или пустые данные'}
            )
        if not request.user.is_authenticated:
            return Response(
                status=UNAUTHORIZED,
                data={'message': 'Пользователь не авторизован'}
            )
        user = request.user
        user.set_password(new_password)
        user.save()
        return Response(
            status=NO_CONTENT,
            data={'message': 'Пароль успешно изменен'})


class PersonalProfileViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    viewsets.GenericViewSet,
):
    """Вью для личного профиля."""

    queryset = User.objects.all()
    serializer_class = UserSelfSerializer
    permission_classes = (IsAuthenticated,)

    def retrieve(self, request):
        """Изменение пользователя."""
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        """Добавление пользователя."""
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
