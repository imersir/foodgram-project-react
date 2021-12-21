from django.contrib import admin
from users.models import User

from .models import Favorite, Follow, Ingredient, IngredientAmount, Recipe, Tag


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk', 'username', 'password',
        'email', 'first_name', 'last_name'
    )
    search_fields = ('username', 'email')
    list_filter = ('username', 'email', 'first_name')
    empty_value_display = '-пусто-'


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


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'author')
    search_fields = ('name', 'author')
    list_filter = ('author', 'name', 'tags')
    inlines = [IngredientAmountInLine]
    empty_value_display = '-пусто-'

    def get_favorited(self, obj):
        return Favorite.objects.filter(recipe=obj).count()


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'color', 'slug')
    search_fields = ('pk', 'name')
    list_filter = ('name', 'slug')
    empty_value_display = '-пусто-'
