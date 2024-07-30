"""Первый более менее рабочий"""


from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
# from django.utils.decorators import method_decorator
# from django.views.decorators.csrf import csrf_exempt
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .serializers import (CustomUserCreateSerializer, UserSelfSerializer,
                          UserSerializer)

User = get_user_model()


# @method_decorator(csrf_exempt, name='dispatch')
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    http_method_names = ['get', 'post']
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return UserSerializer
        elif self.request.method == 'POST':
            return CustomUserCreateSerializer

    @action(methods=['post'], detail=False)
    def set_password(self, request):
        new_password = request.data.get('new_password')
        current_password = request.data.get('current_password')
        if not new_password or not request.user.check_password(
                current_password):
            return Response(
                status=400,
                data={'message': 'Вы ввели неверные или пустые данные'}
            )
        if not request.user.is_authenticated:
            return Response(
                status=401,
                data={'message': 'Пользователь не авторизован'}
            )
        user = request.user
        user.set_password(new_password)
        user.save()
        return Response(status=204, data={'message': 'Пароль успешно изменен'})


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
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request):
        user = get_object_or_404(User, username=request.user.username)
        serializer = self.get_serializer(
            user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        return Response(serializer.data, status=status.HTTP_200_OK)
