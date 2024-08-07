import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from rest_framework import serializers

from .services import create_recipe_ingredients
from foodgram_api.models import (MAX_NUMES, MIN_NUMES, Favorite, Ingredient,
                                 IngredientRecipe, Recipe, ShoppingList,
                                 Subscriptions, Tag)
from users.serializers import UserSelfSerializer

User = get_user_model()
MAX_LENGTH = 200


class Hex2NameColor(serializers.Field):
    """Класс цветов."""

    def to_representation(self, value):
        """Представление."""
        return value

    def to_internal_value(self, data):
        """Валидация."""
        return data


class Base64ImageField(serializers.ImageField):
    """Класс обработки картинок."""

    def to_internal_value(self, data):
        """Обработка картинок."""
        if isinstance(data, str) and data.startswith('data:image'):
            format, imgstr = data.split(';base64,')
            ext = format.split('/')[-1]
            if ext != 'jpeg':
                ext = 'jpeg'
            filename = f'image.{ext}'
            data = ContentFile(base64.b64decode(imgstr), name=filename)
        return super().to_internal_value(data)


class TagSerializer(serializers.ModelSerializer):
    """Сериалайзер для тега."""

    color = Hex2NameColor()

    class Meta:
        """Тонкая настойка класса."""

        model = Tag
        fields = ('id', 'name', 'slug', 'color')


class IngredientSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""

    class Meta:
        """Тонкая настойка класса."""

        model = Ingredient
        fields = (
            'id',
            'name',
            'measurement_unit',
        )


class IngRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),)
    amount = serializers.IntegerField(max_value=MAX_NUMES, min_value=MIN_NUMES)

    class Meta:
        """Тонкая настойка класса."""

        model = IngredientRecipe
        fields = (
            'id',
            'amount'
        )


class RecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    class Meta:
        """Тонкая настойка класса."""

        fields = ('id',
                  'image',
                  'name',
                  'cooking_time')
        model = Recipe


class SubscrPostSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписчиков."""

    user = serializers.SlugRelatedField(
        queryset=User.objects.all(),
        slug_field="username",
        default=serializers.CurrentUserDefault()
    )

    class Meta:
        """Класс тонкой настройки."""

        fields = ('user',)
        model = Subscriptions

    def to_representation(self, instance):
        """Представление."""
        recipes_limit = self.context.get('recipes_limit')
        serializer = UserSelfSerializer(instance.subscribers).data
        recipes = instance.subscribers.author_recipe.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        recipes_list = []
        for recipe in recipes:
            recipe = RecipeSerializer(recipe).data
            recipes_list.append(recipe)
        serializer['recipes'] = recipes_list
        recipes_count = recipes.count()
        serializer['recipes_count'] = recipes_count
        return serializer


class RecipeSerializerGet(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""
    author = UserSelfSerializer()
    ingredients = IngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

    class Meta:
        """Тонкая настойка класса."""

        fields = ['id', 'tags', 'author',
                  'image', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'text', 'cooking_time']
        model = Recipe

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        ing_recipe_instances = IngredientRecipe.objects.filter(
            recipe=instance.id
        )
        ingredients_data = []
        for ing_recipe_instance in ing_recipe_instances:
            ingredient_data = IngredientSerializer(
                ing_recipe_instance.ingredients).data
            ingredient_data['amount'] = ing_recipe_instance.amount
            ingredients_data.append(ingredient_data)
        data['ingredients'] = ingredients_data
        tags = instance.tags.values()
        data['tags'] = tags
        return data


class RecipeSerializerPost(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    image = Base64ImageField()
    ingredients = IngRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField(
        max_value=MAX_NUMES, min_value=MIN_NUMES)
    text = serializers.CharField()
    name = serializers.CharField(max_length=MAX_LENGTH)

    class Meta:
        """Тонкая настойка класса."""

        fields = ['tags', 'image', 'ingredients',
                  'name', 'text', 'cooking_time']
        model = Recipe

    def validate(self, data):
        """Валидация."""
        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Заполните поле ingredients рецепта'
            )
        ingredient_ids = [
            ingredient.get('id').id for ingredient in ingredients
        ]
        existing_ingr_ids = set(
            Ingredient.objects.filter(
                id__in=ingredient_ids
            ).values_list('id', flat=True))
        for ingredient_id in ingredient_ids:
            if ingredient_id not in existing_ingr_ids:
                raise serializers.ValidationError(
                    'Указанный ингредиент не существует'
                )
            if len(existing_ingr_ids) != len(ingredient_ids):
                raise serializers.ValidationError(
                    'Повторяющиеся ingredients'
                )
        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError(
                'Заполните поле tags рецепта'
            )
        tags_ids = [tag.id for tag in tags]
        existing_tag_ids = set(
            Tag.objects.filter(
                id__in=tags_ids
            ).values_list('id', flat=True))
        for tag_id in tags_ids:
            if tag_id not in existing_tag_ids:
                raise serializers.ValidationError(
                    'Указанный tag не существует')
            if len(existing_tag_ids) != len(tags_ids):
                raise serializers.ValidationError(
                    'Повторяющиеся tags'
                )
        return data

    def to_representation(self, instance):
        """Представление."""
        return RecipeSerializerGet(instance).data

    def create(self, validated_data):
        """Создание."""
        user = self.context['request'].user
        validated_data['author'] = user
        ingredients_data = validated_data.pop('ingredients')
        tags_data = validated_data.pop('tags')
        recipe = Recipe.objects.create(**validated_data)
        recipe.tags.set(tags_data)
        create_recipe_ingredients(recipe, ingredients_data)
        return recipe

    def update(self, instance, validated_data):
        instance.author = validated_data.get('author', instance.author)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags_data = validated_data.pop('tags')
        instance.tags.set(tags_data)
        ingredients = validated_data.pop('ingredients')
        instance.ingredients.clear()
        create_recipe_ingredients(instance, ingredients)
        instance.save()
        return instance


class ShoppingListSerializer(serializers.ModelSerializer):
    """Сериалайзер корзины."""

    recipe = RecipeSerializer()

    class Meta:
        """Настойка."""

        model = ShoppingList
        fields = '__all__'


class FavoriteGetSerializer(serializers.ModelSerializer):
    """Сериалайзер для подписчиков."""

    recipe = RecipeSerializer()

    class Meta:
        """Класс тонкой настройки."""

        fields = ('recipe',)
        model = Favorite

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        recipe = data.pop('recipe')
        return recipe


class RecipeFSerializer(serializers.ModelSerializer):
    """Сериалайзер."""

    is_favorited = serializers.BooleanField(read_only=True)

    class Meta:
        """Настройка тонкая."""

        model = Recipe
        fields = '__all__'


class FavoriteSerializer(serializers.ModelSerializer):
    """Сериалайзер избранного."""

    recipe = RecipeSerializer()

    class Meta:
        """Класс тонкой настройки."""

        fields = ('recipe',)
        model = Favorite
