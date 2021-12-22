from django.core.validators import MinValueValidator
from django.db import models

from colorfield.fields import ColorField
from pytils.translit import slugify

from users.models import User


class Ingredient(models.Model):
    name = models.CharField(max_length=200, verbose_name='Название')
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название'
    )
    color = ColorField(
        unique=True,
        default='#FF0000',
        verbose_name='Цвет'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Recipe(models.Model):
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Фото рецепта'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Введите текст'
    )
    ingredients = models.ManyToManyField(
        Ingredient, through='IngredientAmount',
        verbose_name='Ингредиенты'
    )
    tags = models.ManyToManyField(
        'Tag',
        related_name='recipes',
        verbose_name='Теги'
    )
    cooking_time = models.IntegerField(
        verbose_name='Время приготовления в минутах',
        validators=(MinValueValidator(
            1,
            'Минимальное значение времени приготовления '
            'должно быть не меньше минуты'
        ),
        ),
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        db_index=True,
        verbose_name='Дата публикации'
    )

    class Meta:
        ordering = ('name',)
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.text[:15]


class IngredientAmount(models.Model):
    amount = models.PositiveIntegerField(
        validators=(MinValueValidator(
            1, 'Значение ингредиента не может быть меньше 1'
        ),
        ),
    )
    recipe = models.ForeignKey(
        Recipe, on_delete=models.CASCADE,
    )
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.PROTECT,
    )

    class Meta:
        verbose_name = 'Рецепт (количество)'
        constraints = (
            models.UniqueConstraint(
                fields=('recipe', 'ingredient'),
                name='unique_ingredient',
            ),
        )


class Follow(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписаны'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'author'), name='unique_follow'
            ),
        )

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorite_recipe',
        verbose_name='Рецепт',
    )

    class Meta:
        ordering = ('-id',)
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_favourite'
            ),
        )

    def __str__(self):
        return f'Рецепт {self.recipe} добавлен в избранное {self.user}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=('user', 'recipe'),
                name='unique_recipes_in_cart'
            ),
        )
        ordering = ('-id',)
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
