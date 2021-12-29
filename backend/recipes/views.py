from django.http.response import HttpResponse
from django.shortcuts import get_object_or_404

from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .mixins import RetriveAndListViewSet
from .models import (Favorite, Follow, Ingredient, IngredientAmount,
                     Recipe,
                     ShoppingCart, Tag)
from .pagination import CustomPageNumberPaginator
from .permissions import IsAdminOrIsAuthorOrReadOnly
from .serializers import (FavoritesSerializer, FollowSerializer,
                          IngredientsSerializer, RecipeReadSerializer,
                          RecipeSubscriptionSerializer,
                          RecipeWriteSerializer,
                          ShoppingCartSerializer, TagSerializer)


class IngredientsViewSet(RetriveAndListViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientsSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend]
    filterset_class = IngredientFilter
    pagination_class = None


class TagsViewSet(RetriveAndListViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('-id')
    permission_classes = [IsAdminOrIsAuthorOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filter_class = RecipeFilter
    pagination_class = CustomPageNumberPaginator

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeReadSerializer
        return RecipeWriteSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['GET', 'DELETE'],
            url_path='favorite', url_name='favorite',
            permission_classes=[permissions.IsAuthenticated],
            detail=True
            )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        serializer = FavoritesSerializer(
            data={'user': request.user.id, 'recipe': recipe.id}
        )
        if request.method == 'GET':
            serializer.is_valid(raise_exception=True)
            serializer.save(recipe=recipe, user=request.user)
            serializer = RecipeSubscriptionSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        favorite = get_object_or_404(
            Favorite, user=request.user, recipe__id=pk
        )
        favorite.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated, )
    )
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)
        if request.method == 'GET':
            if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
                data = {
                    'errors': 'Этот рецепт уже есть в списке покупок'
                }
                return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
            shopping_cart = ShoppingCart.objects.create(
                user=user, recipe=recipe)
            serializer = ShoppingCartSerializer(
                shopping_cart, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        shopping_cart = ShoppingCart.objects.filter(
            user=user, recipe=recipe
        )
        if not shopping_cart.exists():
            data = {
                'errors': 'Этого рецепта нет в списке покупок'
            }
            return Response(data=data, status=status.HTTP_400_BAD_REQUEST)
        shopping_cart.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    serializer_class = FollowSerializer
    permission_classes = [permissions.IsAuthenticated]
    lookup_field = 'author_id'

    def get_queryset(self):
        user = self.request.user
        return Follow.objects.filter(user=user)

    def perform_create(self, serializer):
        author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
        serializer.save(user=self.request.user, author=author)

    def perform_destroy(self, instance):
        user = self.request.user
        author = get_object_or_404(User, pk=self.kwargs.get('author_id'))
        follow = get_object_or_404(Follow, user=user, author=author)
        follow.delete()


class DownloadShoppingCart(APIView):
    permission_classes = [permissions.IsAuthenticated]
    http_method_names = ['get', ]

    def get(self, request):
        user = request.user
        ingredients = IngredientAmount.objects.filter(
            recipe__shopping_cart__user=user).values_list(
            'ingredient__name', 'amount',
            'ingredient__measurement_unit',
            named=True
        )
        buying_list = {}
        for ingredient in ingredients:
            name = ingredient.ingredient__name
            measurement_unit = ingredient.ingredient__measurement_unit
            amount = ingredient.amount
            if name not in buying_list:
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                buying_list[name]['amount'] += amount

        response = HttpResponse(content_type='application/pdf')
        response['Content-Disposition'] = (
            'attachment; filename="wishlist.pdf"'
        )
        pdfmetrics.registerFont(
            TTFont('sylfaen', '../fonts/sylfaen.ttf')
        )
        c = canvas.Canvas(response)
        c.setFont('sylfaen', 15)
        string = 1
        height = 770
        c.drawString(200, 800, 'Список ингредиентов')
        for item in buying_list:
            c.drawString(100, height, text=(f'{string}. '
                        f'{item} - {buying_list[item]["amount"]} '
                        f'{buying_list[item]["measurement_unit"]} ')
                         )
            height -= 20
            string += 1
        c.showPage()
        c.save()
        return response
