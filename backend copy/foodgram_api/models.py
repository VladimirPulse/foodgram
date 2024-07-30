from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Tag(models.Model):
    name = models.CharField(max_length=64)
    color = models.CharField(max_length=16)
    slug = models.SlugField(
        max_length=52,
        unique=True,
        verbose_name='Идентификатор',
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='название')
    measurement_unit = models.TextField(verbose_name='измеряемая единица')

    class Meta:
        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ['name']

    def __str__(self):
        return self.name


class Recipe(models.Model):
    name = models.CharField(max_length=200, verbose_name='название')
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        User,
        related_name='author',
        on_delete=models.CASCADE,
        verbose_name='автор')
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэги')
    ingredients = models.ManyToManyField(
        Ingredient,
        related_name='ingredients',
        through='IngredientRecipe')
    image = models.ImageField(
        upload_to='images/',
        null=True,
        default=None
    )
    cooking_time = models.IntegerField(
        verbose_name='время приготовления (в минутах)')
    is_favorited = models.BooleanField(
        'избранное', default=False)
    is_in_shopping_cart = models.BooleanField(
        'список покупок', default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class IngredientRecipe(models.Model):
    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField()


class Subscriptions(models.Model):
    """Модель для подписчиков."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="selecting",
        verbose_name='пользователь'
    )
    subscribers = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name="subscribers",
        verbose_name='подписался на'
    )

    class Meta:
        """Уточняющий класс."""
        verbose_name = 'подписчик'
        verbose_name_plural = 'подписчики'

        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscribers"], name="uq_user_subscribers"
            )
        ]


class Favorite(models.Model):
    """Модель для избранного."""

    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE, related_name="favorite",
        verbose_name='рецепт'
    )
    user = models.ForeignKey(
        User,
        related_name='user_favorite',
        on_delete=models.CASCADE,
        verbose_name='пользователь'
    )

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'список избранного'
        ordering = ['user']


class ShoppingList(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        verbose_name='рецепт'
    )

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'список покупок'
        ordering = ['user']
