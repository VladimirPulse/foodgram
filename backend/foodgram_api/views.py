"""Модуль views."""

from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .permissions import IsOwnerOrReadOnly
from .serializers import (IngredientSerializer, RecipeSerializer,
                          RecipeSerializerPost, ShoppingListSerializer,
                          SubscrPostSerializer, TagSerializer)
from .services import ShoppingCartService, ShoppingListDownloadService
from foodgram_api.models import (Favorite, Ingredient, Recipe, ShoppingList,
                                 Subscriptions, Tag)

User = get_user_model()


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс тегов."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (
        permissions.AllowAny,
    )


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Класс ингредиентов."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = None
    permission_classes = (
        permissions.AllowAny,
    )

    def dispatch(self, request, *args, **kwargs):
        """Распределение запросов."""
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        """Запрос ингредиентов."""
        name = self.request.query_params.get('name', None)
        if name:
            queryset = Ingredient.objects.filter(
                name__istartswith=name).order_by('id')
        else:
            queryset = Ingredient.objects.all().order_by('id')
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """Класс для публикаций."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializerPost
    http_method_names = ('get', 'patch', 'post', 'delete')
    permission_classes = (
        IsOwnerOrReadOnly,
    )
    pagination_class = LimitOffsetPagination
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = (
        'author',
        'is_favorited',
        'is_in_shopping_cart'
    )

    def get_queryset(self):
        """Запрос рецептов."""
        queryset = Recipe.objects.all()
        tags = self.request.query_params.getlist('tags')
        if tags:
            tag_ids = Tag.objects.filter(
                slug__in=tags).values_list('id', flat=True)
            queryset = queryset.filter(tags__id__in=tag_ids)
        return queryset


class SubscrViewSet(viewsets.ModelViewSet):
    """Класс для подписчиков."""

    queryset = Subscriptions.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    serializer_class = SubscrPostSerializer
    pagination_class = LimitOffsetPagination
    http_method_names = ('get', 'post', 'delete')

    def list(self, request, *args, **kwargs):
        """Список подписчиков."""
        queryset = self.get_queryset()
        recipes_limit = request.query_params.get('recipes_limit')
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.serializer_class(
                page,
                context={'request': request, 'recipes_limit': recipes_limit},
                many=True)
            return self.get_paginated_response(serializer.data)
        serializer = self.serializer_class(
            queryset,
            context={'request': request, 'recipes_limit': recipes_limit},
            many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def subscribe(self, request, pk=None):
        """Подписчик."""
        user = request.user
        subscribe = get_object_or_404(User, pk=pk)
        if subscribe == user:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscriptions, created = Subscriptions.objects.get_or_create(
            user=user,
            subscribers=subscribe
        )
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        subscribe.is_subscribed = True
        subscribe.save()
        recipes_limit = request.query_params.get('recipes_limit')
        return Response(
            SubscrPostSerializer(
                subscriptions,
                context={'recipes_limit': recipes_limit}).data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def subscribe_delete(self, request, pk=None):
        """Удаление подписчика."""
        subscribe = get_object_or_404(User, pk=pk)
        user = request.user
        try:
            subscription = user.selecting.get(subscribers=subscribe)
        except Subscriptions.DoesNotExist:
            return Response(
                {'error': 'Несуществующая подписка!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        subscription.delete()
        subscribe.is_subscribed = False
        subscribe.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingListViewSet(viewsets.ModelViewSet):
    """Класс списка."""

    queryset = ShoppingList.objects.all()
    serializer_class = ShoppingListSerializer
    permission_classes = (permissions.IsAuthenticated,)
    http_method_names = ('get', 'post', 'delete')

    @action(detail=False, methods=['get'])
    def download_shopping_cart(self, request):
        """Загрузка списка."""
        file_path = ShoppingListDownloadService.download_shopping_list(
            request.user,
        )
        if file_path:
            return FileResponse(open(file_path, 'rb'), as_attachment=True)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'])
    def shopping_cart(self, request, pk=None):
        """Список."""
        try:
            recipe_instance = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Несуществующий рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        added = ShoppingCartService.add_recipe_to_shopping_cart(
            request.user, recipe_instance)
        if added:
            recipe_instance.is_in_shopping_cart = True
            recipe_instance.save()
            return Response(
                RecipeSerializer(added.recipe).data,
                status=status.HTTP_201_CREATED)
        else:
            return Response({
                'error': 'Рецепт уже в корзине покупок'
            }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['delete'])
    def shopping_delete(self, request, pk=None):
        """Удаление списка."""
        recipe = get_object_or_404(Recipe, pk=pk)
        user = request.user
        try:
            shopping = user.user_shopp.get(recipe=recipe)
        except ShoppingList.DoesNotExist:
            return Response(
                {'error': 'Несуществующий список!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        shopping.delete()
        shopping.is_in_shopping_cart = False
        shopping.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FavoriteViewSet(viewsets.ModelViewSet):
    """Класс избранного."""

    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    permission_classes = (permissions.IsAuthenticated,)

    @action(detail=True, methods=['POST'])
    def favorite(self, request, pk=None):
        """Избранное."""
        try:
            recipe = Recipe.objects.get(pk=pk)
        except Recipe.DoesNotExist:
            return Response(
                {'error': 'Несуществующий рецепт!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        user = request.user
        favorite, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe)
        if not created:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        recipe.is_favorited = True
        recipe.save()
        return Response(
            RecipeSerializer(favorite.recipe).data,
            status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['DELETE'])
    def favorite_delete(self, request, pk=None):
        """Удаление избранного."""
        recipe = self.get_object()
        user = request.user
        try:
            favorite = user.user_favorite.get(recipe=recipe)
        except Favorite.DoesNotExist:
            return Response(
                {'error': 'Несуществующее избранное!'},
                status=status.HTTP_400_BAD_REQUEST
            )
        favorite.delete()
        favorite.is_favorited = False
        favorite.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
