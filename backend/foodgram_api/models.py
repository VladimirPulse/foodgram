from django.contrib.auth import get_user_model
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()
MIN_NUMES = 1
MAX_NUMES = 32000


class Tag(models.Model):
    """Модель тегов."""

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
        """Тонкая настройка."""

        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        """Настройка."""
        return self.name


class Ingredient(models.Model):
    """Модель ингридиентов."""

    name = models.CharField(max_length=200, verbose_name='название')
    measurement_unit = models.TextField(verbose_name='измеряемая единица')

    class Meta:
        """Тонкая настройка."""

        verbose_name = 'ингридиент'
        verbose_name_plural = 'ингридиенты'
        ordering = ['name']

    def __str__(self):
        """Настройка."""
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

    name = models.CharField(max_length=200, verbose_name='название')
    text = models.TextField(verbose_name='Описание')
    author = models.ForeignKey(
        User,
        related_name='author_recipe',
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
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='время приготовления (в минутах)',
        validators=[
            MinValueValidator(MIN_NUMES),
            MaxValueValidator(MAX_NUMES)
        ])
    is_favorited = models.BooleanField(
        'избранное', default=False)
    is_in_shopping_cart = models.BooleanField(
        'список покупок', default=False)
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='дата публикации'
    )

    class Meta:
        """Тонкая настройка."""

        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ['-created_at']

    def __str__(self):
        """Настройка."""
        return self.name


class IngredientRecipe(models.Model):
    """Модель ингридиента рецепта."""

    ingredients = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    amount = models.PositiveSmallIntegerField(
        validators=[
            MinValueValidator(MIN_NUMES),
            MaxValueValidator(MAX_NUMES)
        ]
    )

    class Meta:
        """Тонкая настройка."""

        ordering = ['ingredients']

    def __str__(self):
        """Настройка."""
        return self.ingredients.name


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
        ordering = ['subscribers']

        constraints = [
            models.UniqueConstraint(
                fields=["user", "subscribers"], name="uq_user_subscribers"
            )
        ]

    def __str__(self):
        """Настройка."""
        return self.user


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
        """Тонкая настройка."""

        verbose_name = 'избранное'
        verbose_name_plural = 'список избранного'
        ordering = ['user']

    def __str__(self):
        """Настройка."""
        return self.user


class ShoppingList(models.Model):
    """Модель корзины."""

    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='user_shopp',
        verbose_name='пользователь'
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
        related_name='recipe_shopp',
        verbose_name='рецепт'
    )

    class Meta:
        """Тонкая настройка."""

        verbose_name = 'корзина'
        verbose_name_plural = 'список покупок'
        ordering = ['user']

    def __str__(self):
        """Настройка."""
        return self.user
