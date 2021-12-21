from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (DownloadShoppingCart, FollowViewSet, IngredientsViewSet,
                    RecipeViewSet, TagsViewSet)

router = DefaultRouter()

router.register('ingredients', IngredientsViewSet, basename='ingredients')
router.register('recipes', RecipeViewSet, basename='recipe')
router.register('tags', TagsViewSet, basename='tags')


urlpatterns = [
    path('users/<int:author_id>/subscribe/',
         FollowViewSet.as_view({'get': 'create', 'delete': 'destroy'}),
         name='subscribe'),
    path('users/subscriptions/', FollowViewSet.as_view({'get': 'list'}),
         name='subscriptions'),
    path('recipes/download_shopping_cart/',
         DownloadShoppingCart.as_view(), name='dowload_shopping_cart'),
    path('', include(router.urls)),
]
