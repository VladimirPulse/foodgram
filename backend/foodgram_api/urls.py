from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (FavoriteViewSet, IngredientViewSet, RecipeViewSet,
                    ShoppingListViewSet, SubscrViewSet, TagViewSet)

v1_router = DefaultRouter()

v1_router.register(r'tags', TagViewSet, basename='tags')
v1_router.register(r'ingredients', IngredientViewSet, basename='ingredients')
v1_router.register(r'recipes', RecipeViewSet, basename='recipes')
v1_router.register(
    r'users/subscriptions',
    SubscrViewSet,
    basename='subscriptions',
)

urlpatterns = [
    path('recipes/download_shopping_cart/', ShoppingListViewSet.as_view(
        {'get': 'download_shopping_cart'}), name='shopping-download'),
    path('', include(v1_router.urls), name='api-root'),
    path('recipes/<int:pk>/favorite/', FavoriteViewSet.as_view(
        {'post': 'favorite', 'delete': 'favorite_delete'}
    ), name='favorite-recipe'),
    path('users/<int:pk>/subscribe/', SubscrViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe_delete'}
    ), name='subscribe-user'),
    path('recipes/<int:pk>/shopping_cart/', ShoppingListViewSet.as_view(
        {'post': 'shopping_cart', 'delete': 'shopping_delete'}
    ), name='shopping-user'),
]
