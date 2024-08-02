from collections import defaultdict

from django.shortcuts import get_object_or_404

from .models import Ingredient, IngredientRecipe, ShoppingList

# class FavoriteService:
#     """Класс логики избранного."""

#     def add_to_favorites(self, recipe, user):
#         """Добавление избранного."""
#         favorite_obj, created = Favorite.objects.get_or_create(
#             user=user, recipe=recipe)
#         return favorite_obj

#     def remove_from_favorites(self, recipe, user):
#         """Удаление избранного."""
#         Favorite.objects.filter(user=user, recipe=recipe).delete()


# class SubscribeService:
#     """Класс логики подписчиков."""

#     def add_to_favorites(self, subscribers, user):
#         """Добавление подписчиков."""
#         favorite_obj, created = Subscriptions.objects.get_or_create(
#             user=user, subscribers=subscribers)
#         return favorite_obj

#     def remove_from_favorites(self, subscribers, user):
#         """удаление подписчиков."""
#         Subscriptions.objects.filter(
#             user=user, subscribers=subscribers).delete()


class ShoppingCartService:
    """Класс корзины."""

    @staticmethod
    # def add_recipe_to_shopping_cart(user, recipe):
    #     """Добавление в корзину."""
    #     if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
    #         return False
    #     return ShoppingList.objects.create(user=user, recipe=recipe)
    def add_recipe_to_shopping_cart(user, recipe):
        """Добавление в корзину."""
        if user.user_shopp.filter(recipe=recipe).exists():
            return False
        return ShoppingList.objects.create(user=user, recipe=recipe)


class ShoppingListDownloadService:
    """Класс загрузки корзины."""

    @staticmethod
    def generate_shopping_list(user):
        """Создание списка корзины."""
        # shopping_list = ShoppingList.objects.filter(user=user)
        shopping_list = user.user_shopp.all()
        shopping_list_data = defaultdict(int)

        for item in shopping_list:
            ingredients = item.recipe.ingredientrecipe_set.all()
            for ingredient in ingredients:
                shopping_list_data[
                    ingredient.ingredients.name
                ] += ingredient.amount
        return shopping_list_data

    @staticmethod
    def download_shopping_list(user):
        """Загрузка корзины списком."""
        shopping_list_data = (
            ShoppingListDownloadService.generate_shopping_list(user)
        )
        file_path = 'shopping_list.txt'
        with open(file_path, 'w') as file:
            for ingredient, quantity in shopping_list_data.items():
                file.write(f'{ingredient} в количестве {quantity}\n')
        return file_path


def create_recipe_ingredients(recipe, ingredients_data):
    """Создание рецепта."""
    ingredients_to_create = []
    for ingredient_data in ingredients_data:
        ingredient_id = ingredient_data.get('id')
        ingredient = get_object_or_404(Ingredient, id=ingredient_id)
        amount = ingredient_data.get('amount')
        ingredients_to_create.append(IngredientRecipe(
            recipe=recipe,
            ingredients=ingredient,
            amount=amount
        ))
    IngredientRecipe.objects.bulk_create(ingredients_to_create)
