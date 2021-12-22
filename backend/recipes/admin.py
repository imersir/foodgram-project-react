from django.contrib import admin

from foodgram.settings import EMPTY_DISPLAY
from users.models import User

from .models import Favorite, Follow, Ingredient, IngredientAmount, Recipe, Tag


@admin.display(empty_value=EMPTY_DISPLAY)
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'password',
        'email', 'first_name', 'last_name'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email', 'first_name')


class IngredientAmountInLine(admin.TabularInline):
    model = IngredientAmount


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    list_filter = ('name',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('user', 'author')


@admin.display(empty_value=EMPTY_DISPLAY)
@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientAmountInLine]

    def get_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.display(empty_value=EMPTY_DISPLAY)
@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('pk', 'name')
    list_filter = ('name', 'slug')
