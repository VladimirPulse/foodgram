"""Модуль admin."""
from django.contrib import admin

from .models import (Favorite, Ingredient, Recipe, ShoppingList, Subscriptions,
                     Tag)

admin.site.register(Tag)


@admin.register(ShoppingList)
class ShoppingListAdmin(admin.ModelAdmin):
    """Админ корзины."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """Админ избранного."""

    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')


@admin.register(Subscriptions)
class SubscriptionsAdmin(admin.ModelAdmin):
    """Админ подписчиков."""

    list_display = ('user', 'subscribers')
    list_filter = ('user', 'subscribers')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """Админ ингридиента."""

    list_display = ('name', 'measurement_unit')
    list_filter = ('name', )
    search_fields = ('name', )


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """Админ рецепта."""

    list_display = ('name', 'favorite_recipe')
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', )

    def favorite_recipe(self, obj):
        """Избранное."""
        from .models import Favorite
        result = Favorite.objects.filter(recipe=obj).all()
        return result.count()
    favorite_recipe.short_description = 'Сколько раз выбран'
