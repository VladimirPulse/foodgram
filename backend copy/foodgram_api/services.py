from collections import defaultdict

from .models import Favorite, ShoppingList, Subscriptions


class FavoriteService:
    def add_to_favorites(self, recipe, user):
        favorite_obj, created = Favorite.objects.get_or_create(
            user=user, recipe=recipe)
        return favorite_obj

    def remove_from_favorites(self, recipe, user):
        Favorite.objects.filter(user=user, recipe=recipe).delete()


class SubscribeService:
    def add_to_favorites(self, subscribers, user):
        favorite_obj, created = Subscriptions.objects.get_or_create(
            user=user, subscribers=subscribers)
        return favorite_obj

    def remove_from_favorites(self, subscribers, user):
        Subscriptions.objects.filter(
            user=user, subscribers=subscribers).delete()


class ShoppingCartService:
    @staticmethod
    def add_recipe_to_shopping_cart(user, recipe):
        if ShoppingList.objects.filter(user=user, recipe=recipe).exists():
            return False
        obj = ShoppingList.objects.create(user=user, recipe=recipe)
        return obj


class ShoppingListDownloadService:
    @staticmethod
    def generate_shopping_list(user):
        shopping_list = ShoppingList.objects.filter(user=user)
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
        shopping_list_data = (
            ShoppingListDownloadService.generate_shopping_list(user)
        )
        file_path = 'shopping_list.txt'
        with open(file_path, 'w') as file:
            for ingredient, quantity in shopping_list_data.items():
                file.write(f'{ingredient} в количестве {quantity}\n')
        return file_path
