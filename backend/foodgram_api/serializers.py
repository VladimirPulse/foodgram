"""Модуль сериалайзеров."""
import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from foodgram_api.models import (Favorite, Ingredient, IngredientRecipe,
                                 Recipe, ShoppingList, Subscriptions, Tag)
from users.serializers import UserSelfSerializer

User = get_user_model()


def val(data, field, model):
    """Общая валидация."""
    elms_data = data.get(field)
    if elms_data == [] or elms_data is None:
        raise serializers.ValidationError(
            f'Заполните поле {field} рецепта'
        )
    a = []
    for elm_data in elms_data:
        if field == 'ingredients':
            if model.objects.filter(id=elm_data.get('id')).exists():
                a.append(elm_data.get('id'))
            else:
                raise serializers.ValidationError(
                    'Указанный ингридиент не существует'
                )
        else:
            if model.objects.filter(id=elm_data.id).exists():
                a.append(elm_data.id)
            else:
                raise serializers.ValidationError(
                    f'Указанный {field} не существует'
                )
    b = list(set(a))
    if a != b:
        raise serializers.ValidationError(
            f'Повторяющиеся {field}'
        )
    return data


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
            'measurement_unit',)


class IngRecipeSerializer(serializers.ModelSerializer):
    """Сериалайзер для ингридиента."""

    id = serializers.IntegerField()

    class Meta:
        """Тонкая настойка класса."""

        model = IngredientRecipe
        fields = ('id', 'amount')

    def validate_amount(self, value):
        """Валидация."""
        if value < 1:
            raise serializers.ValidationError(
                'Количество ингридиента не может быть меньше 1'
            )
        return value


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
        recipes = instance.subscribers.author.all()
        if recipes_limit:
            recipes = recipes[:int(recipes_limit)]
        recipes_list = []
        for recipe_ecz in recipes:
            recipe = RecipeSerializer(recipe_ecz).data
            recipes_list.append(recipe)
        serializer['recipes'] = recipes_list
        recipes_count = Recipe.objects.filter(
            author=instance.subscribers).count()
        serializer['recipes_count'] = recipes_count
        return serializer


class RecipeSerializerGet(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    author = UserSelfSerializer()
    ingredients = serializers.SerializerMethodField()
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())

    class Meta:
        """Тонкая настойка класса."""

        fields = ['id', 'tags', 'author',
                  'image', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart',
                  'name', 'text', 'cooking_time']
        model = Recipe

    def get_ingredients(self, obj):
        """Запрос по ингридиентам."""
        ing_recipe_instances = IngredientRecipe.objects.filter(recipe=obj.id)
        ingredients_data = []
        for ing_recipe_instance in ing_recipe_instances:
            ingredient_data = IngredientSerializer(
                ing_recipe_instance.ingredients).data
            ingredient_data['amount'] = ing_recipe_instance.amount
            ingredients_data.append(ingredient_data)
        return ingredients_data

    def to_representation(self, instance):
        """Представление."""
        data = super().to_representation(instance)
        tags = instance.tags.values()
        data['tags'] = tags
        return data


class RecipeSerializerPost(serializers.ModelSerializer):
    """Сериалайзер для рецептов."""

    image = Base64ImageField()
    ingredients = IngRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all())
    cooking_time = serializers.IntegerField()
    text = serializers.CharField()
    name = serializers.CharField(max_length=200)

    class Meta:
        """Тонкая настойка класса."""

        fields = ['tags', 'image', 'ingredients',
                  'name', 'text', 'cooking_time']
        model = Recipe

    def validate_cooking_time(self, value):
        """Проверка времени."""
        if value < 1:
            raise serializers.ValidationError(
                'Заполните поле cooking_time рецепта корректно (больше 1)'
            )
        return value

    def validate(self, data):
        """Валидация."""
        val(
            data=data,
            field='ingredients',
            model=Ingredient
        )
        val(
            data=data,
            field='tags',
            model=Tag
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
        for ingredient_data in ingredients_data:
            IngredientRecipe.objects.get_or_create(
                ingredients=get_object_or_404(
                    Ingredient, id=ingredient_data.get('id')),
                recipe=recipe,
                amount=ingredient_data.get('amount')
            )
        return recipe

    def update(self, instance, validated_data):
        """Добавление."""
        instance.author = validated_data.get('author', instance.author)
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time)
        tags_data = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        lst = []
        for ingredient in ingredients:
            current_ingredient, status = (
                IngredientRecipe.objects.get_or_create(
                    ingredients=get_object_or_404(
                        Ingredient, id=ingredient.get('id')),
                    recipe=instance,
                    amount=ingredient.get('amount')))
            lst.append(current_ingredient.ingredients)
        instance.ingredients.set(lst)
        lst_tags = []
        for tag in tags_data:
            lst_tags.append(tag)
        instance.tags.set(lst_tags)
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
